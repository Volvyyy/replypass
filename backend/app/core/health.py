"""
Health Check System for Reply Pass API
Implements 2025 best practices for microservice health monitoring
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from app.config import settings
from app.supabase_client import get_supabase_client
from app.gemini_client import get_gemini_client
from app.stripe_client import get_stripe_client

logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status constants"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyHealthResult:
    """Result of a dependency health check"""

    def __init__(
        self,
        name: str,
        status: str,
        response_time_ms: float,
        error: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        self.name = name
        self.status = status
        self.response_time_ms = response_time_ms
        self.error = error
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "status": self.status,
            "response_time_ms": round(self.response_time_ms, 2),
            "timestamp": self.timestamp,
        }
        if self.error:
            result["error"] = self.error
        if self.details:
            result["details"] = self.details
        return result


class HealthChecker:
    """
    Comprehensive health checking system following 2025 best practices
    """

    def __init__(self):
        self.startup_time = datetime.utcnow()
        self.cache_duration = timedelta(
            seconds=30
        )  # Cache health checks for 30 seconds
        self._cache: Dict[str, Dict] = {}

    async def check_readiness(self) -> Dict[str, Any]:
        """
        Readiness check - verifies critical dependencies are available
        Returns unhealthy if any critical dependency is down
        """
        cache_key = "readiness"
        if self._is_cached(cache_key):
            return self._get_cached(cache_key)

        start_time = time.time()

        # Check critical dependencies in parallel
        tasks = [
            self._check_supabase_connectivity(),
            self._check_database_connectivity(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        dependency_results = []
        overall_status = HealthStatus.HEALTHY

        for result in results:
            if isinstance(result, Exception):
                dependency_results.append(
                    DependencyHealthResult(
                        "unknown", HealthStatus.UNHEALTHY, 0, str(result)
                    )
                )
                overall_status = HealthStatus.UNHEALTHY
            else:
                dependency_results.append(result)
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif (
                    result.status == HealthStatus.DEGRADED
                    and overall_status == HealthStatus.HEALTHY
                ):
                    overall_status = HealthStatus.DEGRADED

        response_time = (time.time() - start_time) * 1000

        health_result = {
            "status": overall_status,
            "service": "reply-pass-api",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time, 2),
            "checks": {
                "critical_dependencies": [dep.to_dict() for dep in dependency_results],
            },
            "summary": {
                "total_checks": len(dependency_results),
                "healthy_checks": len(
                    [d for d in dependency_results if d.status == HealthStatus.HEALTHY]
                ),
                "degraded_checks": len(
                    [d for d in dependency_results if d.status == HealthStatus.DEGRADED]
                ),
                "unhealthy_checks": len(
                    [
                        d
                        for d in dependency_results
                        if d.status == HealthStatus.UNHEALTHY
                    ]
                ),
            },
        }

        self._cache_result(cache_key, health_result)
        return health_result

    async def check_comprehensive(self) -> Dict[str, Any]:
        """
        Comprehensive health check including all dependencies and system metrics
        """
        cache_key = "comprehensive"
        if self._is_cached(cache_key):
            return self._get_cached(cache_key)

        start_time = time.time()

        # Check all dependencies in parallel
        tasks = [
            self._check_supabase_connectivity(),
            self._check_database_connectivity(),
            self._check_gemini_api_connectivity(),
            self._check_stripe_connectivity(),
            self._check_redis_connectivity(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        dependency_results = []
        overall_status = HealthStatus.HEALTHY

        for result in results:
            if isinstance(result, Exception):
                dependency_results.append(
                    DependencyHealthResult(
                        "unknown", HealthStatus.UNHEALTHY, 0, str(result)
                    )
                )
                # Non-critical dependencies (Gemini, Stripe) don't affect overall status
                if (
                    "gemini" not in str(result).lower()
                    and "stripe" not in str(result).lower()
                ):
                    overall_status = HealthStatus.UNHEALTHY
            else:
                dependency_results.append(result)
                # Only critical dependencies affect overall status
                if (
                    result.name in ["supabase", "database"]
                    and result.status == HealthStatus.UNHEALTHY
                ):
                    overall_status = HealthStatus.UNHEALTHY
                elif (
                    result.status == HealthStatus.DEGRADED
                    and overall_status == HealthStatus.HEALTHY
                ):
                    overall_status = HealthStatus.DEGRADED

        response_time = (time.time() - start_time) * 1000

        health_result = {
            "status": overall_status,
            "service": "reply-pass-api",
            "version": "1.0.0",
            "environment": settings.environment,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time, 2),
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
            "checks": {
                "dependencies": [dep.to_dict() for dep in dependency_results],
            },
            "summary": {
                "total_checks": len(dependency_results),
                "healthy_checks": len(
                    [d for d in dependency_results if d.status == HealthStatus.HEALTHY]
                ),
                "degraded_checks": len(
                    [d for d in dependency_results if d.status == HealthStatus.DEGRADED]
                ),
                "unhealthy_checks": len(
                    [
                        d
                        for d in dependency_results
                        if d.status == HealthStatus.UNHEALTHY
                    ]
                ),
            },
            "system_info": {
                "environment": settings.environment,
                "debug_mode": settings.debug_mode,
                "rate_limit_per_minute": settings.basic_rate_limit_per_minute,
                "features": {
                    "supabase_auth": True,
                    "jwt_validation": True,
                    "rate_limiting": True,
                    "security_headers": True,
                    "request_validation": True,
                    "structured_logging": True,
                    "cors_enabled": True,
                },
                "middleware": {
                    "security_headers": "active",
                    "cors": "configured",
                    "rate_limiting": "active",
                    "request_validation": "active",
                    "logging": "active",
                    "compression": "gzip",
                },
            },
        }

        self._cache_result(cache_key, health_result)
        return health_result

    async def _check_supabase_connectivity(self) -> DependencyHealthResult:
        """Check Supabase connectivity and authentication"""
        start_time = time.time()

        try:
            # Test Supabase connection with a simple query
            supabase = get_supabase_client()

            # Try to get service info (this validates the connection and auth)
            response = (
                supabase.table("information_schema.tables")
                .select("table_name")
                .limit(1)
                .execute()
            )

            response_time = (time.time() - start_time) * 1000

            if response.data is not None:
                return DependencyHealthResult(
                    "supabase",
                    HealthStatus.HEALTHY,
                    response_time,
                    details={"connection": "active", "auth": "validated"},
                )
            else:
                return DependencyHealthResult(
                    "supabase",
                    HealthStatus.DEGRADED,
                    response_time,
                    error="No data returned from query",
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Supabase health check failed: {e}")
            return DependencyHealthResult(
                "supabase", HealthStatus.UNHEALTHY, response_time, error=str(e)
            )

    async def _check_database_connectivity(self) -> DependencyHealthResult:
        """Check database connectivity through Supabase"""
        start_time = time.time()

        try:
            # This is essentially the same as Supabase check since we use Supabase as our database
            supabase = get_supabase_client()

            # Test with a simple health check query
            response = supabase.rpc("version").execute()

            response_time = (time.time() - start_time) * 1000

            if response.data:
                return DependencyHealthResult(
                    "database",
                    HealthStatus.HEALTHY,
                    response_time,
                    details={"type": "postgresql", "version": str(response.data)},
                )
            else:
                return DependencyHealthResult(
                    "database",
                    HealthStatus.DEGRADED,
                    response_time,
                    error="Could not get database version",
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Database health check failed: {e}")
            return DependencyHealthResult(
                "database", HealthStatus.UNHEALTHY, response_time, error=str(e)
            )

    async def _check_gemini_api_connectivity(self) -> DependencyHealthResult:
        """Check Gemini API connectivity"""
        start_time = time.time()

        try:
            # Skip if API key is placeholder
            if settings.gemini_api_key.startswith("placeholder"):
                return DependencyHealthResult(
                    "gemini_api",
                    HealthStatus.DEGRADED,
                    0,
                    error="API key not configured",
                    details={"configured": False},
                )

            gemini_client = get_gemini_client()

            # Test with the health check method
            is_healthy = await gemini_client.health_check()

            response_time = (time.time() - start_time) * 1000

            if is_healthy:
                return DependencyHealthResult(
                    "gemini_api",
                    HealthStatus.HEALTHY,
                    response_time,
                    details={
                        "model": settings.default_gemini_model,
                        "configured": True,
                    },
                )
            else:
                return DependencyHealthResult(
                    "gemini_api",
                    HealthStatus.DEGRADED,
                    response_time,
                    error="Health check failed",
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Gemini API health check failed: {e}")
            return DependencyHealthResult(
                "gemini_api", HealthStatus.UNHEALTHY, response_time, error=str(e)
            )

    async def _check_stripe_connectivity(self) -> DependencyHealthResult:
        """Check Stripe API connectivity"""
        start_time = time.time()

        try:
            # Skip if API key is placeholder
            if settings.stripe_secret_key.startswith("placeholder"):
                return DependencyHealthResult(
                    "stripe_api",
                    HealthStatus.DEGRADED,
                    0,
                    error="API key not configured",
                    details={"configured": False},
                )

            stripe_client = get_stripe_client()

            # Test with the health check method
            is_healthy = stripe_client.health_check()

            response_time = (time.time() - start_time) * 1000

            if is_healthy:
                return DependencyHealthResult(
                    "stripe_api",
                    HealthStatus.HEALTHY,
                    response_time,
                    details={"configured": True},
                )
            else:
                return DependencyHealthResult(
                    "stripe_api",
                    HealthStatus.DEGRADED,
                    response_time,
                    error="Health check failed",
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Stripe API health check failed: {e}")
            return DependencyHealthResult(
                "stripe_api", HealthStatus.UNHEALTHY, response_time, error=str(e)
            )

    async def _check_redis_connectivity(self) -> DependencyHealthResult:
        """Check Redis connectivity (when implemented)"""
        start_time = time.time()

        try:
            # Redis is not yet implemented, so we return a placeholder
            response_time = (time.time() - start_time) * 1000

            return DependencyHealthResult(
                "redis",
                HealthStatus.DEGRADED,
                response_time,
                error="Redis not yet implemented",
                details={"configured": False, "planned": True},
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Redis health check failed: {e}")
            return DependencyHealthResult(
                "redis", HealthStatus.UNHEALTHY, response_time, error=str(e)
            )

    def _is_cached(self, key: str) -> bool:
        """Check if health result is cached and still valid"""
        if key not in self._cache:
            return False

        cached_time = self._cache[key].get("cached_at")
        if not cached_time:
            return False

        return datetime.utcnow() - cached_time < self.cache_duration

    def _get_cached(self, key: str) -> Dict[str, Any]:
        """Retrieve cached health result"""
        result = self._cache[key].copy()
        result.pop("cached_at", None)  # Remove internal cache timestamp
        return result

    def _cache_result(self, key: str, result: Dict[str, Any]) -> None:
        """Cache health check result"""
        result_copy = result.copy()
        result_copy["cached_at"] = datetime.utcnow()
        self._cache[key] = result_copy
