import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import starlightLlmsTxt from "starlight-llms-txt";

export default defineConfig({
  site: "https://pylegifrance.github.io",
  base: "/pylegifrance",
  integrations: [
    starlight({
      title: "PyLegifrance",
      logo: { src: "./src/assets/logo.svg" },
      customCss: ["./src/styles/custom.css"],
      defaultLocale: "root",
      locales: {
        root: { label: "Français", lang: "fr" },
        en: { label: "English" },
      },
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/pylegifrance/pylegifrance",
        },
      ],
      editLink: {
        baseUrl:
          "https://github.com/pylegifrance/pylegifrance/edit/main/docs/",
      },
      sidebar: [
        {
          label: "Entités",
          translations: { en: "Entities" },
          autogenerate: { directory: "entities" },
        },
        {
          label: "Concepts",
          translations: { en: "Concepts" },
          autogenerate: { directory: "concepts" },
        },
        {
          label: "Opérations",
          translations: { en: "Operations" },
          autogenerate: { directory: "operations" },
        },
        {
          label: "Référence",
          translations: { en: "Reference" },
          autogenerate: { directory: "references" },
        },
      ],
      plugins: [starlightLlmsTxt()],
    }),
  ],
});
