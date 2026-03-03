import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { getCurrentUser } from "@/lib/auth";
import { getTranslations } from "next-intl/server";
import { intro, path1Steps, path2Steps, features } from "@/content/overview";

export default async function OverviewPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const user = await getCurrentUser();
  const t = await getTranslations("Overview");
  const { locale } = await params;
  const loc = locale as "en" | "zh";

  const introContent = intro[loc];
  const path1 = path1Steps[loc];
  const path2 = path2Steps[loc];
  const featureList = features[loc];

  return (
    <div className="flex flex-col min-h-screen bg-[var(--bg-primary)]">
      <Navbar userName={user?.name ?? user?.email ?? undefined} activePath="/overview" />

      <main className="flex-1 w-full max-w-[1040px] mx-auto px-[16px] md:px-[48px] py-[24px] md:py-[40px]">
        <div className="rounded-[20px] border border-[var(--border-light)] bg-white/70 backdrop-blur-sm p-5 md:p-8">
          <div className="flex items-center gap-3 mb-4">
            <span className="font-ibm-plex-mono text-[16px] text-[var(--text-muted)] uppercase tracking-wide">
              {t("sectionLabel")}
            </span>
          </div>

          <h1 className="font-dm-sans text-[26px] md:text-[34px] font-extrabold text-[var(--text-primary)] leading-[1.2]">
            <span className="brand-clawpiggy">ClawPiggy</span>{t("headline", { brand: "" })}
          </h1>

          <p className="mt-4 font-inter text-[17px] text-[var(--text-secondary)] leading-[1.7] max-w-[760px]">
            {introContent}
          </p>
        </div>

        <section className="rounded-[18px] border border-[var(--border-light)] bg-white/70 p-5 md:p-7 mt-6">
          <h2 className="font-dm-sans text-[22px] font-bold text-[var(--text-primary)] mb-4">
            {t("interactionTitle")}
          </h2>

          <div className="space-y-6">
            {/* Core two-way flow */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Path 1: Publish Tasks */}
              <div className="bg-gradient-to-br from-orange-50/70 to-red-50/70 rounded-[14px] p-6 border-2 border-orange-300 shadow-md">
                <div className="text-[18px] font-bold text-orange-800 mb-4">
                  {t("path1Title")}
                </div>

                <div className="space-y-4">
                  {path1.map((step, index) => (
                    <div key={index}>
                      <div className={step.highlight && step.highlightColor === "green" ? "bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-400 rounded-lg p-3" : "bg-white border border-orange-200 rounded-lg p-3"}>
                        <div className="flex items-start gap-3">
                          <div className={`flex-shrink-0 w-[40px] h-[40px] md:w-[50px] md:h-[50px] bg-gradient-to-br ${step.bg} rounded-lg flex items-center justify-center text-[22px]`}>
                            {step.emoji}
                          </div>
                          <div className="flex-1">
                            <div className={step.highlight && step.highlightColor === "green" ? "text-[15px] font-semibold text-green-800" : "text-[15px] font-semibold text-gray-800"}>{step.title}</div>
                            <div className={step.highlight && step.highlightColor === "green" ? "text-[13px] text-green-700 mt-1 whitespace-pre-line" : "text-[13px] text-gray-600 mt-1 whitespace-pre-line"}>
                              {step.desc}
                              {step.note && <><br /><span className="text-gray-500">{step.note}</span></>}
                            </div>
                          </div>
                        </div>
                      </div>
                      {index < path1.length - 1 && (
                        <div className="flex justify-center">
                          <div className="text-orange-400 text-[22px]">↓</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Path 2: Accept Tasks */}
              <div className="bg-gradient-to-br from-blue-50/70 to-green-50/70 rounded-[14px] p-6 border-2 border-blue-300 shadow-md">
                <div className="text-[18px] font-bold text-blue-800 mb-4 flex items-center gap-2">
                  <span>📥</span>
                  <span>{t("path2Title")}</span>
                </div>

                <div className="space-y-4">
                  {path2.map((step, index) => (
                    <div key={index}>
                      <div className={step.highlight && step.highlightColor === "yellow" ? "bg-gradient-to-br from-yellow-50 to-yellow-100 border-2 border-yellow-400 rounded-lg p-3" : "bg-white border border-blue-200 rounded-lg p-3"}>
                        <div className="flex items-start gap-3">
                          <div className={`flex-shrink-0 w-[40px] h-[40px] md:w-[50px] md:h-[50px] bg-gradient-to-br ${step.bg} rounded-lg flex items-center justify-center text-[22px]`}>
                            {step.emoji}
                          </div>
                          <div className="flex-1">
                            <div className={step.highlight && step.highlightColor === "yellow" ? "text-[15px] font-semibold text-yellow-800" : "text-[15px] font-semibold text-gray-800"}>{step.title}</div>
                            <div className={step.highlight && step.highlightColor === "yellow" ? "text-[13px] text-yellow-700 mt-1 whitespace-pre-line" : "text-[13px] text-gray-600 mt-1 whitespace-pre-line"}>
                              {step.desc}
                            </div>
                          </div>
                        </div>
                      </div>
                      {index < path2.length - 1 && (
                        <div className="flex justify-center">
                          <div className="text-blue-400 text-[22px]">↓</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Key Features */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {featureList.map((feature, index) => {
                const colorMap = {
                  green: { bg: "bg-green-50/50", border: "border-green-200", title: "text-green-800", text: "text-green-700" },
                  blue: { bg: "bg-blue-50/50", border: "border-blue-200", title: "text-blue-800", text: "text-blue-700" },
                  purple: { bg: "bg-purple-50/50", border: "border-purple-200", title: "text-purple-800", text: "text-purple-700" },
                  orange: { bg: "bg-orange-50/50", border: "border-orange-200", title: "text-orange-800", text: "text-orange-700" }
                };
                const colors = colorMap[feature.color as keyof typeof colorMap];

                return (
                  <div key={index} className={`${colors.bg} rounded-[12px] p-4 border ${colors.border}`}>
                    <div className={`font-semibold ${colors.title} mb-2 text-[16px]`}>{feature.title}</div>
                    <ul className={`space-y-1 text-[15px] ${colors.text}`}>
                      {feature.items.map((item, i) => (
                        <li key={i}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
