"use client";

import { useState } from "react";

const DEFAULT_RESTAURANT_IMAGE =
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80";

interface RestaurantImageProps {
  src?: string | null;
  alt: string;
  fallbackSrc?: string;
  className?: string;
}

export default function RestaurantImage({
  src,
  alt,
  fallbackSrc,
  className,
}: RestaurantImageProps) {
  const initialSrc = src || fallbackSrc || DEFAULT_RESTAURANT_IMAGE;
  const [imageSrc, setImageSrc] = useState(initialSrc);

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={className}
      onError={() => {
        if (imageSrc !== DEFAULT_RESTAURANT_IMAGE) {
          setImageSrc(fallbackSrc || DEFAULT_RESTAURANT_IMAGE);
        }
      }}
    />
  );
}
