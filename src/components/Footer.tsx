"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export default function Footer() {
  const t = useTranslations("Footer");
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-auto bg-[var(--bg-footer)] border-t border-[var(--border-footer)]">
      <div className="max-w-[1440px] mx-auto px-[16px] md:px-[48px] py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Left: Brand */}
          <div className="flex items-center gap-2">
            <span className="text-lg">🦞</span>
            <span className="font-ibm-plex-mono text-[16px] font-semibold text-[var(--text-primary)]">
              ClawPiggy
            </span>
            <span className="text-[var(--text-footer)] text-[14px]">
              {t("slogan")}
            </span>
          </div>

          {/* Center: Links */}
          <div className="flex items-center gap-6">
            <Link
              href="/docs"
              className="font-inter text-[15px] text-[var(--text-footer)] hover:text-[var(--text-primary)] transition-colors"
            >
              {t("docs")}
            </Link>
            <a
              className="font-inter text-[15px] text-[var(--text-footer)] hover:text-[var(--text-primary)] transition-colors"
              href="https://github.com/Aubrey-M-ops/credit-trader-secondme"
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
            <Link
              href="/overview"
              className="font-inter text-[15px] text-[var(--text-footer)] hover:text-[var(--text-primary)] transition-colors"
            >
              {t("overview")}
            </Link>
          </div>

          {/* Right: Copyright */}
          <span className="font-inter text-[14px] text-[var(--text-footer)]">
            © {currentYear} clawpiggy. {t("openSource")}
          </span>
        </div>
      </div>
    </footer>
  );
}
