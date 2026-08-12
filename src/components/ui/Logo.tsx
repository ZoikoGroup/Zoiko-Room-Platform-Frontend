"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClientFetch } from "@/lib/api-client";
import { LOGO_UPDATED_EVENT } from "@/lib/branding";

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

    function fetchLogo() {
      apiClientFetch<{ logoUrl: string }>("/api/settings/branding")
        .then((b) => setStoredLogo(b.logoUrl))
        .catch(() => setStoredLogo(""));
    }

    fetchLogo();
    window.addEventListener(LOGO_UPDATED_EVENT, fetchLogo);
    return () => window.removeEventListener(LOGO_UPDATED_EVENT, fetchLogo);
  }, [src]);

  const resolvedSrc = src || storedLogo || DEFAULT_LOGO;

  return (
    <Link href={href} className={`inline-flex items-center ${className ?? ""}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={resolvedSrc} alt="Zoiko Rooms" className={imgClassName ?? "h-9 w-auto object-contain"} />
    </Link>
  );
}
