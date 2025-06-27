/**
 * @deprecated This file is deprecated. Use @/lib/supabase/client instead.
 * @todo Remove this file after migration is complete
 */

import { createClient as createNewClient } from "@/lib/supabase/client";

export function createClient() {
  return createNewClient();
}
