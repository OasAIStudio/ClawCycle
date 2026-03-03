"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Link, usePathname, useRouter } from "@/i18n/routing";
import { useLocale } from "next-intl";
import { GoogleIcon, GitHubIcon } from "@/components/icons";

export default function Navbar({
  userName,
  activePath = "/",
}: {
  userName?: string;
  activePath?: string;
}) {
  const t = useTranslations("Navbar");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [loginOpen, setLoginOpen] = useState(false);

  const navLinks = [
    { href: "/" as const, label: t("home") },
    { href: "/overview" as const, label: t("overview") },
  ];

  function switchLocale() {
    const nextLocale = locale === "en" ? "zh" : "en";
    router.replace(pathname, { locale: nextLocale });
  }

  return (
    <>
    <nav className="sticky top-0 z-50 flex items-center justify-between px-[16px] md:px-[48px] h-[60px] bg-[var(--bg-primary)]/95 backdrop-blur-sm border-b border-[var(--border-light)]">
      {/* Left: Logo */}
      <Link href="/" className="flex items-center gap-[8px] cursor-pointer hover:opacity-80 transition-opacity">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center text-lg shadow-lg shadow-orange-500/20">
          🦞
        </div>
        <div className="flex flex-col">
          <span className="font-ibm-plex-mono text-[18px] font-bold text-[var(--text-primary)] leading-tight">
            ClawPiggy
          </span>
          <span className="text-[12px] text-[var(--text-muted)] leading-tight hidden sm:block">
            {t("tokenMarket")}
          </span>
        </div>
      </Link>

      {/* Center: Nav links */}
      <div className="hidden md:flex items-center gap-1">
        {navLinks.map((link) => {
          const isActive =
            link.href === "/"
              ? activePath === "/"
              : activePath.startsWith(link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`px-4 py-2 rounded-lg font-inter text-[16px] transition-colors ${
                isActive
                  ? "font-semibold text-[var(--accent)] bg-[var(--accent)]/10"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-black/5"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </div>

      {/* Right: Auth + Language Switcher */}
      <div className="flex items-center gap-3">
        {/* Language Switcher */}
        <button
          onClick={switchLocale}
          className="hidden sm:flex items-center px-3 py-1.5 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-black/5 transition-colors font-inter text-[15px] font-medium cursor-pointer"
        >
          {locale === "en" ? "中文" : "EN"}
        </button>

        <a
          href="https://github.com/Aubrey-M-ops/credit-trader-secondme"
          target="_blank"
          rel="noreferrer"
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-black/5 transition-colors"
        >
          <GitHubIcon className="w-4 h-4" />
          <span className="text-[15px] font-medium">GitHub</span>
        </a>

        {userName ? (
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg text-[var(--text-secondary)] hover:bg-black/5 transition-colors"
            >
              <span className="text-sm">👋</span>
              <span className="font-inter text-[16px] max-w-[100px] truncate">{userName}</span>
            </Link>
            {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
            <a
              href="/api/auth/logout"
              className="font-inter text-[15px] text-[var(--text-secondary)] rounded-lg px-4 py-2 border border-[var(--border-medium)] no-underline hover:bg-[var(--bg-tag)] transition-colors"
            >
              {t("logout")}
            </a>
          </div>
        ) : (
          <button
            onClick={() => setLoginOpen(true)}
            className="font-inter text-[15px] font-semibold text-white rounded-lg px-4 py-2 bg-[var(--accent)] hover:opacity-90 transition-opacity cursor-pointer"
          >
            {t("login")}
          </button>
        )}
      </div>
    </nav>

    {loginOpen && (
      <>
        {/* Overlay */}
        <div
          className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm"
          onClick={() => setLoginOpen(false)}
        />
        {/* Modal card */}
        <div className="fixed inset-0 z-[101] flex items-center justify-center pointer-events-none">
          <div className="pointer-events-auto w-[360px] bg-[var(--bg-primary)] rounded-2xl shadow-2xl p-8 flex flex-col gap-6">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <h2 className="font-inter text-[20px] font-bold text-[var(--text-primary)]">
                  {t("loginTitle")}
                </h2>
                <p className="font-inter text-[14px] text-[var(--text-muted)] mt-1">
                  {t("loginSubtitle")}
                </p>
              </div>
              <button
                onClick={() => setLoginOpen(false)}
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors text-[20px] leading-none cursor-pointer"
              >
                ×
              </button>
            </div>

            {/* Login options */}
            <div className="flex flex-col gap-3">
              {/* Google */}
              {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
              <a
                href="/api/auth/login?provider=google"
                className="flex items-center gap-3 font-inter text-[15px] font-medium text-[var(--text-primary)] rounded-xl px-4 py-3 border border-[var(--border-medium)] hover:bg-[var(--bg-tag)] transition-colors"
              >
                <GoogleIcon className="w-5 h-5 shrink-0" />
                Continue with Google
              </a>

              {/* GitHub */}
              {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
              <a
                href="/api/auth/login?provider=github"
                className="flex items-center gap-3 font-inter text-[15px] font-semibold text-white rounded-xl px-4 py-3 bg-[#24292e] hover:bg-[#1a1e22] transition-colors"
              >
                <GitHubIcon className="w-5 h-5 shrink-0" />
                Continue with GitHub
              </a>
            </div>
          </div>
        </div>
      </>
    )}
    </>
  );
}
