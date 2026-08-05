"use client";

import { useEffect, useState } from "react";
import { getCurrentUser, User } from "@/lib/auth";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkSession() {
      const currentUser = await getCurrentUser();

      setUser(currentUser);
      setLoading(false);
    }

    checkSession();
  }, []);

  return {
    user,
    loading,
    isAuthenticated: user !== null,
  };
}
