"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  clearMemories,
  deleteMemory,
  getMemories,
} from "@/lib/api";

import { Memory } from "@/types/memory";

import { useAuth } from "@/lib/useAuth";


export default function SettingsPage() {
  const router = useRouter();

  const {
    loading: authLoading,
    isAuthenticated,
  } = useAuth();

  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [
    authLoading,
    isAuthenticated,
    router,
  ]);


  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    getMemories()
      .then((data) => {
        setMemories(data);
      })
      .catch((error) => {
        console.error(error);
        setError("Failed to load memories.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [isAuthenticated]);


  const handleDelete = async (
    memoryId: number,
  ) => {
    try {
      await deleteMemory(memoryId);

      setMemories((current) =>
        current.filter(
          (memory) => memory.id !== memoryId,
        ),
      );
    } catch (error) {
      console.error(error);
      setError("Failed to delete memory.");
    }
  };


  const handleClear = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to clear all memories?",
    );

    if (!confirmed) {
      return;
    }

    try {
      await clearMemories();

      setMemories([]);
    } catch (error) {
      console.error(error);
      setError("Failed to clear memories.");
    }
  };


  if (authLoading || !isAuthenticated) {
    return (
      <main className="max-w-3xl mx-auto mt-10">
        <p>Checking authentication...</p>
      </main>
    );
  }


  return (
    <main className="min-h-screen bg-gray-50 text-black">
      <div className="max-w-3xl mx-auto px-4 py-8">

        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">
              Settings
            </h1>

            <p className="text-sm text-gray-500 mt-1">
              Manage what AI Workspace remembers.
            </p>
          </div>

          <button
            onClick={() => router.push("/")}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium hover:bg-gray-100"
          >
            Back to chat
          </button>
        </div>


        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold">
                Memory
              </h2>

              <p className="text-sm text-gray-500 mt-1">
                These are persistent preferences or facts
                saved for your account.
              </p>
            </div>

            {memories.length > 0 && (
              <button
                onClick={handleClear}
                className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
              >
                Clear all
              </button>
            )}
          </div>


          {error && (
            <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
              {error}
            </div>
          )}


          {loading ? (
            <p className="text-sm text-gray-500">
              Loading memories...
            </p>
          ) : memories.length === 0 ? (
            <div className="rounded-xl border border-dashed border-gray-300 p-8 text-center">
              <p className="font-medium text-gray-700">
                No memories saved
              </p>

              <p className="text-sm text-gray-500 mt-1">
                Your saved preferences will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {memories.map((memory) => (
                <div
                  key={memory.id}
                  className="flex items-start justify-between gap-4 rounded-xl border border-gray-200 p-4"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-900">
                      {memory.key}
                    </p>

                    <p className="mt-1 text-sm text-gray-600">
                      {memory.value}
                    </p>
                  </div>

                  <button
                    onClick={() =>
                      handleDelete(memory.id)
                    }
                    className="shrink-0 rounded-lg px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}

        </section>
      </div>
    </main>
  );
}