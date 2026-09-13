"use client";

import { useEffect, useState } from "react";
import {
  fetchGeneratedImage,
  generateImage,
} from "@/lib/api";

export default function ImageGenerator() {
  const [prompt, setPrompt] = useState("");
  const [imageUrl, setImageUrl] = useState<string | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(
    null,
  );

  const handleGenerate = async () => {
    const trimmedPrompt = prompt.trim();

    if (!trimmedPrompt || isLoading) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setImageUrl(null);

    try {
      const result =
        await generateImage(trimmedPrompt);
      const imageBlob = await fetchGeneratedImage(
        result.url,
      );

      setImageUrl(
        URL.createObjectURL(imageBlob),
      );
    } catch (error) {
      console.error(
        "Image generation failed:",
        error,
      );

      setError(
        "Failed to generate image. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900">
        Image Generation
      </h2>

      <p className="mt-1 text-sm text-gray-500">
        Describe an image and generate it with AI.
      </p>

      <div className="mt-4 flex gap-2">
        <input
          value={prompt}
          onChange={(event) =>
            setPrompt(event.target.value)
          }
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey
            ) {
              event.preventDefault();
              handleGenerate();
            }
          }}
          disabled={isLoading}
          maxLength={4000}
          placeholder="Describe the image you want..."
          className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
        />

        <button
          type="button"
          onClick={handleGenerate}
          disabled={
            isLoading ||
            !prompt.trim()
          }
          className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading
            ? "Generating..."
            : "Generate"}
        </button>
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-600">
          {error}
        </p>
      )}

      {isLoading && (
        <div className="mt-5 flex h-64 items-center justify-center rounded-xl border border-gray-200 bg-gray-50">
          <p className="text-sm text-gray-500">
            Generating image...
          </p>
        </div>
      )}

      {imageUrl && !isLoading && (
        <div className="mt-5">
          <img
            src={imageUrl}
            alt={prompt}
            className="max-h-150 w-full rounded-xl object-contain"
          />
        </div>
      )}
    </section>
  );
}