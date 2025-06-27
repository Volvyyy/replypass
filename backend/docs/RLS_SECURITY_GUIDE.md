# Row Level Security (RLS) Implementation Guide

## Overview

This document describes the Row Level Security (RLS) implementation for Reply Pass, ensuring proper tenant isolation and data security in our multi-user Supabase environment.

## Table of Contents

1. [Security Architecture](#security-architecture)
2. [RLS Policy Implementation](#rls-policy-implementation)
3. [Testing and Verification](#testing-and-verification)
4. [Performance Considerations](#performance-considerations)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Security Architecture

### Core Principles

1. **Tenant Isolation**: Each user can only access their own data
2. **Principle of Least Privilege**: Users get minimum necessary permissions
3. **Defense in Depth**: Multiple security layers (RLS + application logic)
4. **Audit Trail**: All sensitive operations are logged

### Authentication Flow

```
User Login → Supabase Auth → JWT Token → RLS Policy Evaluation → Data Access
```

### Security Boundaries

- **User Boundary**: `auth.uid()` ensures user isolation
- **Service Boundary**: `auth.role() = 'service_role'` for admin operations
- **Data Boundary**: Foreign key relationships maintain data integrity

## RLS Policy Implementation

### 1. Users Table

```sql
-- Users can manage their own profile
CREATE POLICY "Users can manage own profile" ON users
FOR ALL USING (auth.uid()::text = auth_id);

-- Authenticated users can view basic profile info
CREATE POLICY "Users can view others basic profile" ON users
FOR SELECT USING (
    auth.role() = 'authenticated' AND
    id != auth.uid() AND
    NOT (profile ? 'private_data' OR profile ? 'internal_notes')
);
```

**Security Features:**
- ✅ User isolation via `auth.uid()`
- ✅ Prevents access to sensitive profile fields
- ✅ Service role administrative access

### 2. Cases Table

```sql
-- Users manage their own cases
CREATE POLICY "Users can manage own cases" ON cases
FOR ALL USING (user_id = auth.uid()::uuid AND deleted_at IS NULL);

-- Enhanced security policy
CREATE POLICY "Secure case metadata access" ON cases
FOR SELECT USING (
    user_id = auth.uid()::uuid AND
    deleted_at IS NULL AND
    NOT (metadata->>'is_sensitive' = 'true' AND auth.role() != 'service_role')
);
```

**Security Features:**
- ✅ User isolation via `user_id = auth.uid()`
- ✅ Soft delete awareness
- ✅ Sensitive data protection
- ✅ Rate limiting for case creation

### 3. Conversation Data

```sql
-- Messages inherit security from conversation logs
CREATE POLICY "Users can manage messages through conversation logs" ON conversation_messages
FOR ALL USING (
    EXISTS (
        SELECT 1 FROM conversation_logs cl
        JOIN cases c ON c.id = cl.case_id
        WHERE cl.id = conversation_log_id
        AND c.user_id = auth.uid()::uuid 
        AND c.deleted_at IS NULL
        AND NOT (metadata->>'is_sensitive' = 'true' AND auth.role() != 'service_role')
    )
);
```

**Security Features:**
- ✅ Hierarchical security inheritance
- ✅ Sensitive conversation protection
- ✅ Partition-aware policies

### 4. Generated Replies and Suggestions

```sql
-- Replies inherit from cases with usage tracking
CREATE POLICY "Users can manage generated replies through cases" ON generated_replies
FOR ALL USING (
    EXISTS (
        SELECT 1 FROM cases c
        WHERE c.id = case_id
        AND c.user_id = auth.uid()::uuid 
        AND c.deleted_at IS NULL
    )
    AND
    EXISTS (
        SELECT 1 FROM usage_logs ul
        WHERE ul.user_id = auth.uid()::uuid
        AND ul.usage_type = 'reply_generation'
        AND ul.metadata->>'generated_reply_id' = id::text
    )
);
```

**Security Features:**
- ✅ Case-based inheritance
- ✅ Usage tracking validation
- ✅ Prevents unauthorized reply access

### 5. Subscription and Usage Data

```sql
-- Users can only view their own subscriptions
CREATE POLICY "Users can view own subscriptions" ON user_subscriptions
FOR SELECT USING (
    user_id = auth.uid()::uuid AND
    (auth.role() = 'service_role' OR stripe_subscription_id IS NOT NULL)
);

-- Usage logs are immutable
CREATE POLICY "Prevent usage log tampering" ON usage_logs
FOR UPDATE USING (false);

CREATE POLICY "Prevent usage log deletion" ON usage_logs
FOR DELETE USING (false);
```

**Security Features:**
- ✅ Subscription data protection
- ✅ Immutable audit logs
- ✅ Prevents data tampering

## Advanced Security Features

### 1. Audit Trail

```sql
-- Audit sensitive operations
CREATE OR REPLACE FUNCTION audit_sensitive_operation(
    operation_type varchar,
    table_name varchar,
    record_id uuid,
    details jsonb DEFAULT '{}'
)
RETURNS void AS $$
BEGIN
    INSERT INTO usage_logs (user_id, usage_type, metadata)
    VALUES (
        auth.uid()::uuid,
        'security_audit',
        jsonb_build_object(
            'operation', operation_type,
            'table', table_name,
            'record_id', record_id,
            'details', details,
            'ip_address', current_setting('request.headers', true)::jsonb->>'x-forwarded-for',
            'user_agent', current_setting('request.headers', true)::jsonb->>'user-agent'
        )
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 2. Subscription-Based Access Control

```sql
-- Check subscription permissions
CREATE OR REPLACE FUNCTION check_subscription_access(operation_type varchar)
RETURNS boolean AS $$
DECLARE
    user_plan record;
BEGIN
    SELECT sp.features INTO user_plan
    FROM user_subscriptions us
    JOIN subscription_plans sp ON sp.id = us.plan_id
    WHERE us.user_id = auth.uid()::uuid
    AND us.status IN ('active', 'trialing')
    ORDER BY us.created_at DESC
    LIMIT 1;
    
    IF NOT FOUND THEN
        RETURN operation_type IN ('basic_reply_generation', 'text_input');
    END IF;
    
    RETURN (user_plan.features ? operation_type) OR 
           (user_plan.features->>'tier' = 'unlimited');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3. Performance Optimization

```sql
-- Materialized view for RLS optimization
CREATE MATERIALIZED VIEW user_case_access AS
SELECT 
    c.id as case_id,
    c.user_id,
    c.deleted_at IS NULL as is_active
FROM cases c
WHERE c.deleted_at IS NULL;

-- Automatic refresh trigger
CREATE TRIGGER refresh_user_case_access_trigger
    AFTER INSERT OR UPDATE OR DELETE ON cases
    FOR EACH STATEMENT EXECUTE FUNCTION refresh_user_case_access();
```

## Testing and Verification

### 1. Automated Testing

Run the RLS policy test suite:

```bash
cd backend
python -m pytest tests/test_rls_policies.py -v
```

### 2. Security Verification Script

```bash
cd backend
python scripts/verify_rls_policies.py
```

This script provides:
- ✅ Comprehensive security audit
- ✅ Policy coverage analysis
- ✅ Performance recommendations
- ✅ Security scoring (0-100)

### 3. Manual Testing Scenarios

1. **User Isolation Test**
   - Create test users
   - Verify data isolation
   - Test cross-user access attempts

2. **Privilege Escalation Test**
   - Test role-based access
   - Verify service role permissions
   - Test unauthorized operations

3. **Data Integrity Test**
   - Test soft delete functionality
   - Verify audit trail logging
   - Test constraint enforcement

## Performance Considerations

### 1. RLS Policy Optimization

- **Materialized Views**: Used for complex join operations
- **Partial Indexes**: Optimized for active data only
- **Policy Caching**: PostgreSQL 17 optimizations
- **Query Planning**: Efficient execution paths

### 2. Index Strategy

```sql
-- User-based indexes for RLS
CREATE INDEX idx_cases_user_active ON cases (user_id, created_at DESC) 
    WHERE deleted_at IS NULL;

-- Covering indexes for common queries
CREATE INDEX idx_reply_suggestions_covering ON reply_suggestions(generated_reply_id, category) 
    INCLUDE (suggestion, was_sent, partner_reaction);
```

### 3. Monitoring

Key metrics to monitor:
- RLS policy evaluation time
- Query execution plans
- Index usage statistics
- Cache hit ratios

## Troubleshooting

### Common Issues

1. **"Permission Denied" Errors**
   ```sql
   -- Check if RLS is enabled
   SELECT relname, relrowsecurity FROM pg_class WHERE relname = 'your_table';
   
   -- Check policies
   SELECT * FROM pg_policies WHERE tablename = 'your_table';
   ```

2. **Performance Issues**
   ```sql
   -- Analyze query performance
   EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM your_table WHERE condition;
   
   -- Check policy complexity
   SELECT policyname, qual FROM pg_policies WHERE tablename = 'your_table';
   ```

3. **Data Access Issues**
   ```sql
   -- Verify user authentication
   SELECT auth.uid(), auth.role();
   
   -- Test policy conditions manually
   SELECT * FROM your_table WHERE user_id = auth.uid()::uuid;
   ```

### Debug Mode

Enable RLS debugging:

```sql
-- Enable statement logging
SET log_statement = 'all';
SET log_min_duration_statement = 0;

-- Show RLS policy evaluation
SET row_security = on;
SET debug_print_plan = on;
```

## Best Practices

### 1. Policy Design

- ✅ **Keep policies simple**: Complex policies hurt performance
- ✅ **Use appropriate indexes**: Support RLS filter conditions
- ✅ **Leverage inheritance**: Reduce policy duplication
- ✅ **Test thoroughly**: Every policy should have tests

### 2. Security Principles

- ✅ **Default deny**: No access unless explicitly granted
- ✅ **Audit everything**: Log sensitive operations
- ✅ **Regular reviews**: Periodic security audits
- ✅ **Monitor performance**: Watch for policy overhead

### 3. Development Workflow

1. **Design Phase**: Plan RLS strategy early
2. **Implementation**: Write policies with tests
3. **Testing**: Comprehensive security testing
4. **Deployment**: Gradual rollout with monitoring
5. **Maintenance**: Regular audits and updates

### 4. Production Considerations

- **Backup Strategy**: Ensure RLS policies are backed up
- **Monitoring**: Set up alerts for security violations
- **Performance**: Regular performance reviews
- **Updates**: Keep PostgreSQL and Supabase updated

## Migration Checklist

When deploying RLS policies:

- [ ] All tables have RLS enabled
- [ ] User isolation policies implemented
- [ ] Service role access configured
- [ ] Audit logging functional
- [ ] Performance benchmarks met
- [ ] Test suite passing
- [ ] Documentation updated
- [ ] Security review completed

## Support and Resources

- **Supabase RLS Documentation**: https://supabase.com/docs/guides/auth/row-level-security
- **PostgreSQL RLS Documentation**: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **Internal Security Team**: Contact for security reviews
- **Performance Team**: Contact for optimization guidance

---

**Last Updated**: 2025-06-27  
**Version**: 1.0  
**Next Review**: 2025-07-27