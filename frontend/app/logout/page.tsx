"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/auth";

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    logout();

    localStorage.removeItem("chatId");

    router.replace("/login");
  }, [router]);

  return (
    <main className="max-w-md mx-auto mt-20 p-6 text-center">
      {" "}
      <p>Logging out...</p>{" "}
    </main>
  );
}
