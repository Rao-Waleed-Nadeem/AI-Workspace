"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getCurrentUser, login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    

    setError("");
    setIsLoading(true);

    try {
      await login(email, password);

      console.log("Login attempt 1 with email:", email); // Debugging line

      const user = await getCurrentUser();

      console.log("Login attempt 2 with email:", user); // Debugging line

      if (!user) {
        throw new Error(
          "Login succeeded, but the session could not be verified.",
        );
      }

      router.push("/");
    } catch (error) {
      setError(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="max-w-md mx-auto mt-20 p-6">
      {" "}
      <h1 className="text-3xl font-bold mb-2">AI Workspace </h1>
      <p className="text-gray-600 mb-6">Login to your account</p>
      <form onSubmit={handleLogin} className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          className="w-full border rounded-lg px-4 py-2"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          className="w-full border rounded-lg px-4 py-2"
        />

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? "Logging in..." : "Login"}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        Don't have an account?{" "}
        <Link href="/register" className="text-blue-600 hover:underline">
          Register
        </Link>
      </p>
    </main>
  );
}
