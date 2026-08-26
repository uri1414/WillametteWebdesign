# -*- coding: utf-8 -*-
"""
Per-service content for the /services/<slug>/ pages, EN + ES.

SEO-PLAYBOOK.md section 1: one page per service someone actually searches for
individually -- never a template with only the service name swapped. Each
page gets its own real intro, its own FAQ angle, and its own upsell framing
into the Willamette 30-Day Program, because none of these sell standalone:
there is no per-service price anywhere in site.config.json, only the $799
bundle and $99/month ongoing management. The upsell section on every page
says so honestly rather than implying a separate checkout that doesn't exist.
"""

SERVICES = [
    {
        "slug": "website-design",
        "name": "Website Design",
        "en": {
            "title": "Website Design Services | Willamette Web Design",
            "description": ("Custom, mobile-first websites for Willamette Valley "
                            "businesses — fast, built to convert, and SEO-ready "
                            "from day one. Bilingual. See what's included."),
            "h1": "Website Design for Willamette Valley Businesses",
            "lead": ("A fast, mobile-first website built to turn visitors into "
                     "customers — not a template with your logo swapped in."),
            "intro": [
                ("Most small-business websites fail at one job: turning a "
                 "visitor into a phone call or a booked estimate. A slow "
                 "site, a cluttered homepage, or a contact form nobody finds "
                 "costs real business every week it stays live. We build "
                 "sites the way the rest of this site is built — "
                 "fast-loading, mobile-first, and structured around the one "
                 "thing a visitor actually came to do."),
                ("This is for a Willamette Valley business that either has "
                 "no website yet or has one that's slow, outdated, or was "
                 "never built to bring in leads in the first place. Every "
                 "site ships in English, and in Spanish as a real, "
                 "separately-written page — not a translation plugin bolted "
                 "on after."),
            ],
            "included": [
                "Custom design built for your business, not a drag-and-drop template",
                "Mobile-first layout — most local searches happen on a phone",
                "Fast page loads: optimized images, no bloated page builders",
                "Clear calls to action — phone, form, and directions where they belong",
                "Built on the same technical foundation as every page of this site: real HTML, self-hosted fonts, no render-blocking scripts",
            ],
            "why_us": [
                ("Real code, not a locked-in builder",
                 "No proprietary drag-and-drop platform holding your site "
                 "hostage — you own what gets built."),
                ("SEO-ready from day one",
                 "Titles, structured data, and page speed are part of the "
                 "build, not an upsell added later."),
                ("Bilingual by default",
                 "A genuine Spanish version at its own URL, not a machine "
                 "translation — see Local SEO for why that matters for "
                 "search."),
            ],
            "faq": [
                ("Do I own the website once it's built?",
                 "Yes — the site and its content are yours. Ownership "
                 "details are spelled out in the agreement."),
                ("Can you redesign a site I already have?",
                 "Yes. Most of our builds replace an existing site rather "
                 "than starting from nothing."),
                ("How long does a website alone take?",
                 "On its own, timeline depends on scope. Inside the 30-Day "
                 "Program, the site goes live in the first week alongside "
                 "everything else — see the Program page for the exact "
                 "schedule."),
                ("Is hosting included?",
                 "Yes, as part of the ongoing $99/month management after "
                 "the site launches."),
            ],
            "upsell_h": "A website alone rarely brings in customers by itself.",
            "upsell_b": ("It still needs a Google Business Profile, local "
                        "listings that match, and a way for leads to "
                        "actually reach you — the same systems the "
                        "Willamette 30-Day Program builds alongside it. The "
                        "full program is $799 one-time, often less than "
                        "what a website alone costs elsewhere."),
        },
        "es": {
            "title": "Diseño de Sitios Web | Willamette Web Design",
            "description": ("Sitios web personalizados y diseñados primero para "
                            "el celular para negocios del valle de Willamette — "
                            "rápidos y hechos para convertir."),
            "h1": "Diseño de Sitios Web para Negocios del Valle de Willamette",
            "lead": ("Un sitio web rápido, diseñado primero para el celular, "
                     "hecho para convertir visitantes en clientes — no una "
                     "plantilla con tu logo pegado encima."),
            "intro": [
                ("La mayoría de los sitios web de negocios pequeños fallan "
                 "en una sola cosa: convertir a un visitante en una llamada "
                 "o una cita agendada. Un sitio lento, una página de inicio "
                 "desordenada o un formulario de contacto que nadie "
                 "encuentra cuesta negocio real cada semana que sigue así. "
                 "Construimos sitios de la misma forma en que está "
                 "construido el resto de este sitio — rápidos, diseñados "
                 "primero para el celular, y estructurados alrededor de lo "
                 "único que un visitante realmente vino a hacer."),
                ("Esto es para un negocio del valle de Willamette que no "
                 "tiene sitio web todavía, o que tiene uno lento, "
                 "desactualizado, o que nunca fue construido para generar "
                 "clientes potenciales. Cada sitio se entrega en inglés, y "
                 "en español como una página real, escrita por separado — "
                 "no un plugin de traducción pegado después."),
            ],
            "included": [
                "Diseño personalizado para tu negocio, no una plantilla genérica",
                "Diseño primero para el celular — la mayoría de las búsquedas locales pasan ahí",
                "Carga rápida: imágenes optimizadas, sin constructores de páginas pesados",
                "Llamadas a la acción claras — teléfono, formulario y direcciones donde deben estar",
                "Construido sobre la misma base técnica que cada página de este sitio: HTML real, fuentes propias, sin scripts que bloqueen la carga",
            ],
            "why_us": [
                ("Código real, no un constructor que te ata",
                 "Ninguna plataforma propietaria de arrastrar y soltar "
                 "reteniendo tu sitio — lo que se construye es tuyo."),
                ("Listo para SEO desde el día uno",
                 "Títulos, datos estructurados y velocidad de carga son "
                 "parte de la construcción, no un extra que se agrega "
                 "después."),
                ("Bilingüe por defecto",
                 "Una versión en español real, en su propia URL, no una "
                 "traducción automática — mira SEO Local para entender por "
                 "qué eso importa para las búsquedas."),
            ],
            "faq": [
                ("¿Soy dueño del sitio web una vez construido?",
                 "Sí — el sitio y su contenido son tuyos. Los detalles de "
                 "propiedad están especificados en el acuerdo."),
                ("¿Pueden rediseñar un sitio que ya tengo?",
                 "Sí. La mayoría de nuestros proyectos reemplazan un sitio "
                 "existente en lugar de empezar desde cero."),
                ("¿Cuánto tarda un sitio web por sí solo?",
                 "Por sí solo, el tiempo depende del alcance. Dentro del "
                 "Programa de 30 Días, el sitio queda en línea en la "
                 "primera semana junto con todo lo demás — mira la página "
                 "del Programa para el calendario exacto."),
                ("¿El hosting está incluido?",
                 "Sí, como parte de la gestión continua de $99/mes después "
                 "del lanzamiento del sitio."),
            ],
            "upsell_h": "Un sitio web solo rara vez trae clientes por sí mismo.",
            "upsell_b": ("Todavía necesita un Perfil de Negocio de Google, "
                        "directorios locales que coincidan, y una forma de "
                        "que los clientes potenciales realmente te "
                        "contacten — los mismos sistemas que el Programa de "
                        "30 Días de Willamette construye junto con él. El "
                        "programa completo cuesta $799 pago único, "
                        "frecuentemente menos de lo que cuesta un sitio web "
                        "solo en otro lugar."),
        },
    },
    {
        "slug": "local-seo",
        "name": "Local SEO",
        "en": {
            "title": "Local SEO Services | Willamette Web Design",
            "description": ("Local SEO for Willamette Valley businesses — "
                            "on-page optimization, structured data, and "
                            "technical SEO built around how people actually "
                            "search nearby."),
            "h1": "Local SEO Services for Willamette Valley Businesses",
            "lead": ("Getting found for the searches that actually bring in "
                     "customers — \"[service] near me\" and \"[service] in "
                     "[city].\""),
            "intro": [
                ("Local SEO is different from general SEO: the goal isn't "
                 "ranking everywhere, it's ranking for the searches a "
                 "nearby customer actually types — a service plus a city, "
                 "or a service plus \"near me.\" That means page structure, "
                 "metadata, and local signals matter more than chasing "
                 "broad keywords no local business can realistically win."),
                ("Every page on this site is built against the same "
                 "handbook: unique titles and descriptions, structured data "
                 "that matches what's visible on the page, and page speed "
                 "treated as a ranking factor, not an afterthought. That's "
                 "the same foundation a local SEO engagement builds for "
                 "your site."),
            ],
            "included": [
                "On-page SEO foundation: unique titles, meta descriptions, and heading structure per page",
                "Schema.org structured data (Service, LocalBusiness, FAQPage) so search engines understand the page, not just read it",
                "Technical SEO: page speed, mobile-friendliness, and crawlability",
                "Local keyword targeting built around real search intent, not a keyword repeated into every paragraph",
                "A sitemap and internal linking structure so no page is an orphan",
            ],
            "why_us": [
                ("No fabricated trust signals",
                 "No invented reviews, no fake urgency counters — Google "
                 "penalizes exactly this, and it isn't how we'd want to be "
                 "found either."),
                ("Every claim matches what's on the page",
                 "Structured data is generated from the visible content "
                 "itself, so it can't quietly drift out of sync."),
                ("Built for the whole valley",
                 "City-specific pages for the towns we serve, plus a "
                 "valley-wide hub for the rest — see Service Areas."),
            ],
            "faq": [
                ("How long until I see results?",
                 "Local SEO compounds — expect meaningful movement over "
                 "months, not days. Anyone promising a guaranteed timeline "
                 "isn't being straight with you."),
                ("Do you guarantee rankings?",
                 "No — no honest SEO service can guarantee a specific "
                 "ranking. What we guarantee is a technically sound, "
                 "honestly built foundation."),
                ("Can you improve an existing site's SEO without a full redesign?",
                 "Often, yes — it depends on what the current site is "
                 "built on. Worth a real look before assuming a rebuild is "
                 "required."),
                ("Is this different from a Google Business Profile?",
                 "Related but different: your Google Business Profile is "
                 "your listing on Google Maps and local search; local SEO "
                 "is what makes your actual website rank. Most businesses "
                 "need both — see Google Business Profile Setup."),
            ],
            "upsell_h": "SEO works best paired with the systems it's driving traffic to.",
            "upsell_b": ("A well-optimized page that leads to a slow site "
                        "or a missing Google listing loses the visitor "
                        "anyway. The 30-Day Program builds the SEO "
                        "foundation alongside the website, the Google "
                        "Business Profile, and lead capture — one "
                        "connected system for $799, instead of solving "
                        "each piece separately."),
        },
        "es": {
            "title": "Servicios de SEO Local | Willamette Web Design",
            "description": ("SEO local para negocios del valle de Willamette — "
                            "optimización en la página y datos estructurados, "
                            "construido para cómo la gente busca cerca."),
            "h1": "Servicios de SEO Local para Negocios del Valle de Willamette",
            "lead": ("Que te encuentren en las búsquedas que realmente traen "
                     "clientes — \"[servicio] cerca de mí\" y \"[servicio] en "
                     "[ciudad].\""),
            "intro": [
                ("El SEO local es diferente del SEO general: la meta no es "
                 "aparecer en todas partes, es aparecer en las búsquedas "
                 "que un cliente cercano realmente escribe — un servicio "
                 "más una ciudad, o un servicio más \"cerca de mí\". Eso "
                 "significa que la estructura de la página, los metadatos y "
                 "las señales locales importan más que perseguir palabras "
                 "clave amplias que ningún negocio local puede ganar "
                 "realmente."),
                ("Cada página de este sitio está construida bajo el mismo "
                 "manual: títulos y descripciones únicos, datos "
                 "estructurados que coinciden con lo visible en la página, "
                 "y velocidad de carga tratada como factor de "
                 "posicionamiento, no como algo secundario. Esa es la misma "
                 "base que un servicio de SEO local construye para tu "
                 "sitio."),
            ],
            "included": [
                "Base de SEO en la página: títulos, descripciones y estructura de encabezados únicos por página",
                "Datos estructurados de Schema.org (Service, LocalBusiness, FAQPage) para que los buscadores entiendan la página, no solo la lean",
                "SEO técnico: velocidad de carga, compatibilidad con celular y rastreabilidad",
                "Palabras clave locales basadas en intención de búsqueda real, no repetidas en cada párrafo",
                "Un mapa del sitio y estructura de enlaces internos para que ninguna página quede huérfana",
            ],
            "why_us": [
                ("Sin señales de confianza fabricadas",
                 "Sin reseñas inventadas, sin contadores de urgencia "
                 "falsos — Google penaliza exactamente esto, y tampoco es "
                 "cómo queremos que nos encuentren."),
                ("Cada afirmación coincide con lo que está en la página",
                 "Los datos estructurados se generan desde el contenido "
                 "visible, así que no pueden desalinearse en silencio."),
                ("Construido para todo el valle",
                 "Páginas específicas para las ciudades que atendemos, más "
                 "un centro para todo el valle — mira Áreas de Servicio."),
            ],
            "faq": [
                ("¿Cuánto tardaré en ver resultados?",
                 "El SEO local se acumula con el tiempo — espera avances "
                 "reales en meses, no en días. Quien prometa un plazo "
                 "garantizado no te está diciendo la verdad."),
                ("¿Garantizan posiciones en Google?",
                 "No — ningún servicio de SEO honesto puede garantizar una "
                 "posición específica. Lo que garantizamos es una base "
                 "técnicamente sólida y construida con honestidad."),
                ("¿Pueden mejorar el SEO de un sitio existente sin rediseñarlo?",
                 "Frecuentemente sí — depende de sobre qué está construido "
                 "el sitio actual. Vale la pena revisarlo antes de asumir "
                 "que se necesita reconstruir todo."),
                ("¿Esto es diferente de un Perfil de Negocio de Google?",
                 "Relacionado pero diferente: tu Perfil de Negocio de "
                 "Google es tu listado en Google Maps y búsquedas locales; "
                 "el SEO local es lo que hace que tu sitio web mismo "
                 "aparezca. La mayoría de los negocios necesitan ambos — "
                 "mira Configuración de Perfil de Negocio de Google."),
            ],
            "upsell_h": "El SEO funciona mejor junto a los sistemas hacia los que dirige tráfico.",
            "upsell_b": ("Una página bien optimizada que lleva a un sitio "
                        "lento o a un listado de Google incompleto pierde "
                        "al visitante de todos modos. El Programa de 30 "
                        "Días construye la base de SEO junto con el sitio "
                        "web, el Perfil de Negocio de Google y la captura "
                        "de clientes — un sistema conectado por $799, en "
                        "lugar de resolver cada parte por separado."),
        },
    },
    {
        "slug": "google-business-profile",
        "name": "Google Business Profile Setup",
        "en": {
            "title": "Google Business Profile Setup | Willamette Web Design",
            "description": ("Google Business Profile setup and optimization for "
                            "Willamette Valley businesses — the single "
                            "highest-leverage step in local search, done "
                            "right."),
            "h1": "Google Business Profile Setup & Optimization",
            "lead": ("Often the single highest-leverage thing a local "
                     "business can fix — and the most commonly "
                     "half-finished."),
            "intro": [
                ("A Google Business Profile is frequently the first thing a "
                 "potential customer sees — before your website, sometimes "
                 "before they even know your business exists. An unclaimed "
                 "profile, the wrong category, inconsistent hours, or zero "
                 "photos quietly costs calls every day it stays that way."),
                ("Setup means claiming or correcting the profile, choosing "
                 "categories that actually match what you do, and making "
                 "sure the name, address, and phone number match your "
                 "website and every directory exactly — a mismatch there "
                 "is one of the more common reasons a real business ranks "
                 "below competitors with a fraction of the reputation."),
            ],
            "included": [
                "Claim or take over an unclaimed or mismanaged profile",
                "Correct business categories and service area configuration",
                "Complete every profile field Google offers — hours, services, attributes, description",
                "Photo upload guidance so the profile doesn't sit empty",
                "NAP (name, address, phone) checked to match your website and listings exactly",
            ],
            "why_us": [
                ("NAP consistency is enforced, not just promised",
                 "This site's own build process fails automatically if a "
                 "phone number or name drifts anywhere on it — the same "
                 "discipline applies to your profile."),
                ("No fake reviews, ever",
                 "We won't generate or broker fake reviews. A real "
                 "review-generation process is part of the ongoing "
                 "relationship, not a shortcut."),
                ("Service-area businesses done right",
                 "We know the difference between a storefront listing and "
                 "a service-area profile — get it wrong and Google can "
                 "suspend the listing entirely."),
            ],
            "faq": [
                ("I already have a Google Business Profile — can you just optimize it?",
                 "Yes — most engagements start with an existing profile "
                 "that's incomplete or has drifted out of sync, not a "
                 "blank one."),
                ("How long does Google take to verify a profile?",
                 "Verification timing is Google's call, not ours — usually "
                 "days, sometimes longer depending on the method Google "
                 "offers for your business."),
                ("Do you handle getting reviews for me?",
                 "We can set up the process and the ask — but every "
                 "review has to be real. See the guarantee section on the "
                 "homepage for how proof and reviews get handled honestly."),
                ("What if my business doesn't have a physical storefront?",
                 "That's the majority of the businesses we work with, "
                 "including this one — a service-area profile with no "
                 "public address, set up correctly, is completely "
                 "legitimate to Google."),
            ],
            "upsell_h": "A great Google listing still needs a website behind it.",
            "upsell_b": ("Someone who finds you on Google Maps still clicks "
                        "through expecting a real site — and the listings "
                        "and local SEO that got them there in the first "
                        "place. The 30-Day Program sets all of it up "
                        "together for $799, instead of a profile fix that "
                        "leads to a site that isn't ready for the traffic."),
        },
        "es": {
            "title": "Configuración de Perfil de Google | Willamette Web Design",
            "description": ("Configuración y optimización de Perfil de Negocio "
                            "de Google para negocios del valle de Willamette — "
                            "el paso de mayor impacto en búsquedas locales, "
                            "hecho bien."),
            "h1": "Configuración y Optimización del Perfil de Negocio de Google",
            "lead": ("Frecuentemente lo más importante que un negocio local "
                     "puede corregir — y lo más comúnmente dejado a medias."),
            "intro": [
                ("Un Perfil de Negocio de Google suele ser lo primero que "
                 "ve un cliente potencial — antes que tu sitio web, a "
                 "veces antes de saber siquiera que tu negocio existe. Un "
                 "perfil sin reclamar, la categoría equivocada, horarios "
                 "inconsistentes o cero fotos cuesta llamadas en silencio "
                 "cada día que sigue así."),
                ("Configurarlo significa reclamar o corregir el perfil, "
                 "elegir las categorías que realmente coinciden con lo que "
                 "haces, y asegurarte de que el nombre, la dirección y el "
                 "teléfono coincidan exactamente con tu sitio web y cada "
                 "directorio — un desajuste ahí es una de las razones más "
                 "comunes por las que un negocio real aparece debajo de "
                 "competidores con una fracción de su reputación."),
            ],
            "included": [
                "Reclamar o tomar control de un perfil sin reclamar o mal gestionado",
                "Corregir categorías del negocio y configuración del área de servicio",
                "Completar cada campo que Google ofrece — horarios, servicios, atributos, descripción",
                "Guía para subir fotos, para que el perfil no quede vacío",
                "Verificación de que el nombre, dirección y teléfono coincidan exactamente con tu sitio web y directorios",
            ],
            "why_us": [
                ("La consistencia del NAP se exige, no solo se promete",
                 "El proceso de construcción de este mismo sitio falla "
                 "automáticamente si un teléfono o nombre se desalinea en "
                 "cualquier parte — la misma disciplina aplica a tu "
                 "perfil."),
                ("Nunca reseñas falsas",
                 "No generamos ni conseguimos reseñas falsas. Un proceso "
                 "real de generación de reseñas es parte de la relación "
                 "continua, no un atajo."),
                ("Negocios de área de servicio hechos bien",
                 "Sabemos la diferencia entre un listado con local físico "
                 "y un perfil de área de servicio — hacerlo mal puede "
                 "hacer que Google suspenda el listado por completo."),
            ],
            "faq": [
                ("Ya tengo un Perfil de Negocio de Google — ¿pueden solo optimizarlo?",
                 "Sí — la mayoría de nuestros proyectos empiezan con un "
                 "perfil existente incompleto o desalineado, no uno en "
                 "blanco."),
                ("¿Cuánto tarda Google en verificar un perfil?",
                 "El tiempo de verificación lo decide Google, no "
                 "nosotros — usualmente días, a veces más dependiendo del "
                 "método que Google ofrezca para tu negocio."),
                ("¿Ustedes consiguen las reseñas por mí?",
                 "Podemos configurar el proceso y la solicitud — pero cada "
                 "reseña tiene que ser real. Mira la sección de garantía "
                 "en la página de inicio para ver cómo manejamos las "
                 "pruebas y reseñas con honestidad."),
                ("¿Qué pasa si mi negocio no tiene un local físico?",
                 "Esa es la mayoría de los negocios con los que "
                 "trabajamos, incluido este — un perfil de área de "
                 "servicio sin dirección pública, configurado "
                 "correctamente, es completamente legítimo para Google."),
            ],
            "upsell_h": "Un buen listado de Google todavía necesita un sitio web detrás.",
            "upsell_b": ("Alguien que te encuentra en Google Maps igual "
                        "espera hacer clic y ver un sitio real — y los "
                        "directorios y el SEO local que lo llevaron ahí "
                        "primero. El Programa de 30 Días configura todo "
                        "junto por $799, en lugar de arreglar solo el "
                        "perfil y dejarlo con un sitio que no está listo "
                        "para el tráfico."),
        },
    },
    {
        "slug": "local-listings-citations",
        "name": "Local Listings & Citations",
        "en": {
            "title": "Local Listings & Citations | Willamette Web Design",
            "description": ("Consistent business listings across Yelp, "
                            "Nextdoor, Apple Business Connect, Bing Places, "
                            "and Facebook — matching NAP everywhere it "
                            "counts."),
            "h1": "Local Business Listings & Citations",
            "lead": ("Your business name, address, and phone number, "
                     "consistent everywhere a customer or a search engine "
                     "might look."),
            "intro": [
                ("A citation is any place your business is listed online "
                 "with your name, address, and phone number — Yelp, "
                 "Nextdoor, Apple Business Connect, Bing Places, Facebook, "
                 "and dozens of smaller directories. Search engines use "
                 "how consistently that information appears across the web "
                 "as a trust signal; a mismatched phone number on even one "
                 "directory can quietly work against every other listing."),
                ("This is usually invisible work until it's wrong — most "
                 "business owners have no idea an old address or a former "
                 "phone number is still live on a directory they forgot "
                 "existed. Getting it right the first time, and keeping it "
                 "right, is the actual job."),
            ],
            "included": [
                "Submission to the major directories: Yelp, Nextdoor, Apple Business Connect, Bing Places, Facebook Business Page",
                "NAP audit against your website and Google Business Profile",
                "Correction of existing listings with outdated or inconsistent information",
                "A record of where your business is listed, so nothing has to be rediscovered later",
            ],
            "why_us": [
                ("We check, not assume",
                 "An audit of existing listings comes first — fixing "
                 "what's wrong matters as much as adding what's missing."),
                ("Built on the same standard as this site",
                 "Every phone number and address on willametteweb.com "
                 "itself is enforced to match exactly — the same "
                 "discipline applies to your listings."),
                ("No directory left guessing",
                 "Consistent categories and descriptions across every "
                 "listing, not just the name and number."),
            ],
            "faq": [
                ("Which directories actually matter?",
                 "It depends on your industry, but Yelp, Nextdoor, Apple "
                 "Business Connect, Bing Places, and Facebook cover the "
                 "ones that move the needle for most local service "
                 "businesses."),
                ("I think I already have listings out there — can you find them?",
                 "Yes — an audit of what already exists, correct or not, "
                 "is the first step before adding anything new."),
                ("How long does this take?",
                 "Submission is quick; some directories take longer than "
                 "others to actually publish or verify a listing, which is "
                 "outside our control."),
                ("Does this replace a Google Business Profile?",
                 "No — Google Business Profile is its own, separate, "
                 "higher-priority piece. See Google Business Profile "
                 "Setup."),
            ],
            "upsell_h": "Listings work best once there's a real site and profile to send people to.",
            "upsell_b": ("Citations point people somewhere — they're only "
                        "as useful as what's waiting for them. The 30-Day "
                        "Program builds the listings alongside the website "
                        "and Google Business Profile they're meant to "
                        "support, for $799 total."),
        },
        "es": {
            "title": "Directorios y Citas Locales | Willamette Web Design",
            "description": ("Listados de negocio consistentes en Yelp, "
                            "Nextdoor, Apple Business Connect, Bing Places y "
                            "Facebook — con el mismo nombre, dirección y "
                            "teléfono en todos lados."),
            "h1": "Directorios y Citas Locales para tu Negocio",
            "lead": ("El nombre, la dirección y el teléfono de tu negocio, "
                     "consistentes en todos los lugares donde un cliente o "
                     "un buscador puedan mirar."),
            "intro": [
                ("Una cita (citation) es cualquier lugar donde tu negocio "
                 "aparece listado en línea con tu nombre, dirección y "
                 "teléfono — Yelp, Nextdoor, Apple Business Connect, Bing "
                 "Places, Facebook, y docenas de directorios más pequeños. "
                 "Los buscadores usan qué tan consistente es esa "
                 "información en toda la web como señal de confianza; un "
                 "teléfono desalineado en un solo directorio puede jugar "
                 "en contra de todos los demás listados en silencio."),
                ("Este suele ser trabajo invisible hasta que algo está "
                 "mal — la mayoría de los dueños de negocio no tienen idea "
                 "de que una dirección vieja o un teléfono anterior sigue "
                 "activo en un directorio que ya olvidaron que existía. "
                 "Hacerlo bien desde el principio, y mantenerlo así, es el "
                 "trabajo real."),
            ],
            "included": [
                "Publicación en los directorios principales: Yelp, Nextdoor, Apple Business Connect, Bing Places, Facebook Business Page",
                "Auditoría del NAP contra tu sitio web y tu Perfil de Negocio de Google",
                "Corrección de listados existentes con información desactualizada o inconsistente",
                "Un registro de dónde está listado tu negocio, para no tener que redescubrirlo después",
            ],
            "why_us": [
                ("Revisamos, no asumimos",
                 "Una auditoría de los listados existentes va primero — "
                 "corregir lo que está mal importa tanto como agregar lo "
                 "que falta."),
                ("Construido bajo el mismo estándar que este sitio",
                 "Cada teléfono y dirección en willametteweb.com mismo "
                 "está obligado a coincidir exactamente — la misma "
                 "disciplina aplica a tus directorios."),
                ("Ningún directorio se queda adivinando",
                 "Categorías y descripciones consistentes en cada listado, "
                 "no solo el nombre y el número."),
            ],
            "faq": [
                ("¿Cuáles directorios realmente importan?",
                 "Depende de tu industria, pero Yelp, Nextdoor, Apple "
                 "Business Connect, Bing Places y Facebook cubren los que "
                 "más impactan para la mayoría de los negocios locales de "
                 "servicio."),
                ("Creo que ya tengo listados por ahí — ¿pueden encontrarlos?",
                 "Sí — una auditoría de lo que ya existe, correcto o no, "
                 "es el primer paso antes de agregar algo nuevo."),
                ("¿Cuánto tarda esto?",
                 "La publicación es rápida; algunos directorios tardan más "
                 "que otros en realmente publicar o verificar un listado, "
                 "lo cual está fuera de nuestro control."),
                ("¿Esto reemplaza al Perfil de Negocio de Google?",
                 "No — el Perfil de Negocio de Google es su propia pieza, "
                 "separada y de mayor prioridad. Mira Configuración de "
                 "Perfil de Negocio de Google."),
            ],
            "upsell_h": "Los directorios funcionan mejor cuando hay un sitio y un perfil reales a dónde enviar a la gente.",
            "upsell_b": ("Los directorios apuntan a algún lado — solo son "
                        "tan útiles como lo que espera del otro lado. El "
                        "Programa de 30 Días construye los directorios "
                        "junto con el sitio web y el Perfil de Negocio de "
                        "Google que están hechos para apoyar, por $799 en "
                        "total."),
        },
    },
    {
        "slug": "social-media-setup",
        "name": "Social Media Setup",
        "en": {
            "title": "Social Media Setup | Willamette Web Design",
            "description": ("Social media profiles set up right for Willamette "
                            "Valley businesses — the right platforms, "
                            "connected to your website and Google listing."),
            "h1": "Social Media Setup for Local Businesses",
            "lead": ("The right profiles, set up once, connected to the "
                     "rest of your online presence — not a dozen accounts "
                     "nobody maintains."),
            "intro": [
                ("Most small businesses don't need to be everywhere — they "
                 "need to be set up correctly on the one or two platforms "
                 "their actual customers use, with a profile that matches "
                 "the website and the Google listing instead of "
                 "contradicting them. A half-finished, disconnected "
                 "profile can cost more trust than having no profile at "
                 "all."),
                ("Setup means claiming the right handles, matching "
                 "branding and business information across platforms, and "
                 "linking everything back to the real website — not "
                 "building a following from scratch, which is a longer, "
                 "separate conversation."),
            ],
            "included": [
                "Profile setup or claim on the platforms that match your business",
                "Branding and business information consistent with your website and Google Business Profile",
                "Bio and link-in-bio pointed at the real website, not a placeholder",
                "Guidance on which platforms are actually worth maintaining for your industry",
            ],
            "why_us": [
                ("Consistency over quantity",
                 "A correctly set-up profile on the platforms that matter "
                 "beats a dozen abandoned accounts."),
                ("Connected, not isolated",
                 "Profiles link back to the same website and match the "
                 "same Google Business Profile — one presence, not several "
                 "disconnected ones."),
                ("Honest about what this is and isn't",
                 "Setup, not ongoing content management or ad management — "
                 "we'll say so plainly rather than overselling it."),
            ],
            "faq": [
                ("Do you post content or run ads for me?",
                 "Setup covers getting the profiles right, not ongoing "
                 "content creation — that's a separate conversation if "
                 "it's something you want."),
                ("Which platforms do I actually need?",
                 "It depends on your industry and customers — part of "
                 "setup is a straight answer on what's worth your time, "
                 "not signing you up for everything."),
                ("Can you fix profiles I already started and abandoned?",
                 "Yes — cleaning up and connecting an existing but "
                 "neglected profile is common."),
                ("Is this part of the 30-Day Program?",
                 "Yes — social presence setup is one of the eight things "
                 "every 30-Day Program includes."),
            ],
            "upsell_h": "Social profiles work best as part of one connected presence.",
            "upsell_b": ("On their own, social profiles rarely drive "
                        "business — paired with a real website, a complete "
                        "Google listing, and matching local listings, they "
                        "become one more path back to you instead of a "
                        "dead end. That's the whole 30-Day Program, for "
                        "$799."),
        },
        "es": {
            "title": "Configuración de Redes Sociales | Willamette Web Design",
            "description": ("Perfiles de redes sociales configurados "
                            "correctamente para negocios del valle de "
                            "Willamette — conectados a tu sitio web y tu "
                            "perfil de Google."),
            "h1": "Configuración de Redes Sociales para Negocios Locales",
            "lead": ("Los perfiles correctos, configurados una vez, "
                     "conectados al resto de tu presencia en línea — no una "
                     "docena de cuentas que nadie mantiene."),
            "intro": [
                ("La mayoría de los negocios pequeños no necesitan estar en "
                 "todas partes — necesitan estar bien configurados en una "
                 "o dos plataformas que sus clientes reales usan, con un "
                 "perfil que coincide con el sitio web y el perfil de "
                 "Google en lugar de contradecirlos. Un perfil a medias y "
                 "desconectado puede costar más confianza que no tener "
                 "perfil en absoluto."),
                ("Configurarlo significa reclamar los usuarios correctos, "
                 "hacer coincidir la marca e información del negocio en "
                 "todas las plataformas, y conectar todo de vuelta al "
                 "sitio web real — no construir seguidores desde cero, que "
                 "es una conversación más larga y separada."),
            ],
            "included": [
                "Configuración o reclamo de perfil en las plataformas que coinciden con tu negocio",
                "Marca e información del negocio consistente con tu sitio web y tu Perfil de Negocio de Google",
                "Biografía y enlace apuntando al sitio web real, no a un placeholder",
                "Orientación sobre qué plataformas realmente valen la pena mantener para tu industria",
            ],
            "why_us": [
                ("Consistencia sobre cantidad",
                 "Un perfil bien configurado en las plataformas que "
                 "importan vale más que una docena de cuentas abandonadas."),
                ("Conectado, no aislado",
                 "Los perfiles conectan de vuelta al mismo sitio web y "
                 "coinciden con el mismo Perfil de Negocio de Google — una "
                 "sola presencia, no varias desconectadas."),
                ("Honestos sobre lo que esto es y no es",
                 "Configuración, no gestión continua de contenido o "
                 "anuncios — lo decimos claramente en lugar de "
                 "exagerarlo."),
            ],
            "faq": [
                ("¿Publican contenido o manejan anuncios por mí?",
                 "La configuración cubre dejar los perfiles bien hechos, "
                 "no la creación continua de contenido — eso es una "
                 "conversación separada si es algo que quieres."),
                ("¿Cuáles plataformas realmente necesito?",
                 "Depende de tu industria y tus clientes — parte de la "
                 "configuración es una respuesta honesta sobre qué vale tu "
                 "tiempo, no inscribirte en todo."),
                ("¿Pueden arreglar perfiles que ya empecé y abandoné?",
                 "Sí — limpiar y conectar un perfil existente pero "
                 "descuidado es algo común."),
                ("¿Esto es parte del Programa de 30 Días?",
                 "Sí — la configuración de presencia social es una de las "
                 "ocho cosas que incluye cada Programa de 30 Días."),
            ],
            "upsell_h": "Los perfiles sociales funcionan mejor como parte de una sola presencia conectada.",
            "upsell_b": ("Por sí solos, los perfiles sociales rara vez "
                        "traen negocio — junto a un sitio web real, un "
                        "perfil de Google completo y directorios locales "
                        "consistentes, se convierten en un camino más de "
                        "vuelta a ti en lugar de un callejón sin salida. "
                        "Eso es el Programa de 30 Días completo, por $799."),
        },
    },
]

HUB = {
    "en": {
        "title": "Web Design & Local SEO Services | Willamette Web Design",
        "description": ("Website design, local SEO, Google Business Profile "
                        "setup, local listings, and social media setup for "
                        "Willamette Valley businesses — or get all five, "
                        "bundled."),
        "eyebrow": "SERVICES",
        "h1": "Web Design & Local SEO Services",
        "lead": ("Five pieces of a complete local presence, each explained "
                 "on its own page — or all five together, for less, in the "
                 "Willamette 30-Day Program."),
        "intro": ("We don't usually sell these one at a time — nearly every "
                  "project runs through the bundled 30-Day Program, because "
                  "a website without local SEO behind it, or a Google "
                  "listing with no website to send people to, rarely works "
                  "on its own. But if you're trying to understand exactly "
                  "what one piece involves, here's each one, honestly."),
        "grid_kicker": "THE FIVE SERVICES",
        "grid_heading": "What's involved, one piece at a time",
        "card_cta": "See details",
        "bundle_kicker": "OR GET EVERYTHING, FOR LESS",
        "bundle_heading": "All five, plus three more, for $799.",
        "bundle_body": ("The Willamette 30-Day Program bundles every "
                        "service on this page — plus lead capture, "
                        "analytics, and ongoing support — into one 30-day "
                        "build for $799 one-time, then $99/month if you "
                        "want ongoing management after that."),
        "bundle_cta": "See how the 30-Day Program works",
        "apply_cta": "Apply for the 30-Day Program",
        "check_cta": "Get a free presence check",
        "trust_bilingual": "English & Español",
    },
    "es": {
        "title": "Servicios de Diseño Web y SEO Local | Willamette Web Design",
        "description": ("Diseño web, SEO local, Perfil de Negocio de Google, "
                        "directorios locales y redes sociales para negocios "
                        "del valle de Willamette — o los cinco juntos."),
        "eyebrow": "SERVICIOS",
        "h1": "Servicios de Diseño Web y SEO Local",
        "lead": ("Cinco piezas de una presencia local completa, cada una "
                 "explicada en su propia página — o las cinco juntas, por "
                 "menos, en el Programa de 30 Días de Willamette."),
        "intro": ("Normalmente no vendemos esto por separado — casi todos "
                  "los proyectos pasan por el Programa de 30 Días completo, "
                  "porque un sitio web sin SEO local detrás, o un perfil de "
                  "Google sin sitio web a dónde enviar a la gente, rara vez "
                  "funciona por sí solo. Pero si quieres entender "
                  "exactamente qué implica una sola pieza, aquí está cada "
                  "una, con honestidad."),
        "grid_kicker": "LOS CINCO SERVICIOS",
        "grid_heading": "Qué implica, una pieza a la vez",
        "card_cta": "Ver detalles",
        "bundle_kicker": "O CONSIGUE TODO, POR MENOS",
        "bundle_heading": "Los cinco, más tres más, por $799.",
        "bundle_body": ("El Programa de 30 Días de Willamette combina cada "
                        "servicio de esta página — más captura de "
                        "clientes, analítica y soporte continuo — en una "
                        "construcción de 30 días por $799 pago único, y "
                        "luego $99/mes si quieres gestión continua después."),
        "bundle_cta": "Ve cómo funciona el Programa de 30 Días",
        "apply_cta": "Aplica al Programa de 30 Días",
        "check_cta": "Obtén una revisión de presencia gratis",
        "trust_bilingual": "Inglés y Español",
    },
}
