"use client";

import { useEffect, useRef, useState } from "react";

type VoiceAudioPlayerProps = {
  audioChunks: string[];
};

export default function VoiceAudioPlayer({
  audioChunks,
}: VoiceAudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlsRef = useRef<string[]>([]);

  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /*
   * Convert Base64 audio chunks into browser object URLs.
   */
  useEffect(() => {
    const urls = audioChunks.map((chunk) => {
      const binary = atob(chunk);

      const bytes = new Uint8Array(binary.length);

      for (let index = 0; index < binary.length; index += 1) {
        bytes[index] = binary.charCodeAt(index);
      }

      const blob = new Blob([bytes], {
        type: "audio/wav",
      });

      return URL.createObjectURL(blob);
    });

    audioUrlsRef.current = urls;

    setCurrentChunkIndex(0);
    setIsPlaying(false);
    setIsLoading(false);
    setError(null);

    return () => {
      urls.forEach((url) => {
        URL.revokeObjectURL(url);
      });

      audioUrlsRef.current = [];
    };
  }, [audioChunks]);

  /*
   * Cleanup when the component disappears.
   */
  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      audioRef.current = null;
    };
  }, []);

  const stopAudio = () => {
    const audio = audioRef.current;

    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }

    setIsPlaying(false);
    setIsLoading(false);
    setCurrentChunkIndex(0);
  };

  const playCurrentChunk = async () => {
    const url = audioUrlsRef.current[currentChunkIndex];

    if (!url) {
      return;
    }

    const audio = new Audio(url);

    audioRef.current = audio;

    audio.onended = () => {
      const nextChunkIndex = currentChunkIndex + 1;

      if (
        nextChunkIndex <
        audioUrlsRef.current.length
      ) {
        setCurrentChunkIndex(nextChunkIndex);
        setIsLoading(false);
        setIsPlaying(true);
      } else {
        setIsPlaying(false);
        setIsLoading(false);
        setCurrentChunkIndex(0);
        audioRef.current = null;
      }
    };

    audio.onerror = () => {
      setIsPlaying(false);
      setIsLoading(false);
      setError("Audio playback failed.");
      audioRef.current = null;
    };

    setError(null);
    setIsLoading(true);

    try {
      await audio.play();

      setIsLoading(false);
      setIsPlaying(true);
    } catch (playbackError) {
      console.error(
        "Audio playback failed:",
        playbackError,
      );

      setIsLoading(false);
      setIsPlaying(false);

      setError(
        "The browser blocked audio playback. Press Play again.",
      );

      audioRef.current = null;
    }
  };

  const handlePlayPause = async () => {
    const audio = audioRef.current;

    if (audio) {
      if (audio.paused) {
        try {
          setError(null);
          setIsLoading(true);

          await audio.play();

          setIsLoading(false);
          setIsPlaying(true);
        } catch (playbackError) {
          console.error(
            "Audio resume failed:",
            playbackError,
          );

          setIsLoading(false);
          setIsPlaying(false);

          setError(
            "The browser blocked audio playback. Press Play again.",
          );
        }

        return;
      }

      audio.pause();
      setIsPlaying(false);

      return;
    }

    await playCurrentChunk();
  };

  if (audioChunks.length === 0) {
    return null;
  }

  return (
    <div className="mt-2 flex flex-wrap items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 p-2">
      <button
        type="button"
        onClick={handlePlayPause}
        disabled={isLoading}
        className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isLoading
          ? "Loading..."
          : isPlaying
            ? "⏸ Pause"
            : "▶ Play"}
      </button>

      <button
        type="button"
        onClick={stopAudio}
        disabled={
          isLoading === false &&
          isPlaying === false &&
          currentChunkIndex === 0
        }
        className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
      >
        ⏹ Stop
      </button>

      {error && (
        <span className="text-sm text-red-600">
          {error}
        </span>
      )}

      {!error && (
        <span className="text-xs text-gray-500">
          Voice response
        </span>
      )}
    </div>
  );
}