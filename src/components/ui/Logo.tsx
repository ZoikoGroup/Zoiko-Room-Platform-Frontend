"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getLogoUrl, LOGO_UPDATED_EVENT } from "@/lib/branding";

const DEFAULT_LOGO = "/logo.webp";

interface LogoProps {
  src?: string;
  href?: string;
  variant?: "dark" | "light";
  className?: string;
  imgClassName?: string;
}

export function Logo({ src, href = "/", className, imgClassName }: LogoProps) {
  const [storedLogo, setStoredLogo] = useState("");

  useEffect(() => {
    if (src) return;
    setStoredLogo(getLogoUrl());
    const onUpdate = () => setStoredLogo(getLogoUrl());
    window.addEventListener(LOGO_UPDATED_EVENT, onUpdate);
    window.addEventListener("storage", onUpdate);
    return () => {
      window.removeEventListener(LOGO_UPDATED_EVENT, onUpdate);
      window.removeEventListener("storage", onUpdate);
    };
  }, [src]);

  const resolvedSrc = src || storedLogo || DEFAULT_LOGO;

  return (
    <Link href={href} className={`inline-flex items-center ${className ?? ""}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={resolvedSrc} alt="Zoiko Rooms" className={imgClassName ?? "h-9 w-auto object-contain"} />
    </Link>
  );
}
