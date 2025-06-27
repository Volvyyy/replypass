/**
 * @deprecated This file is deprecated. Use @/lib/supabase/server instead.
 * @todo Remove this file after migration is complete
 */

import {
  createClient as createNewClient,
  getCurrentUser,
} from "@/lib/supabase/server";

export async function createClient() {
  return createNewClient();
}

export { getCurrentUser };
