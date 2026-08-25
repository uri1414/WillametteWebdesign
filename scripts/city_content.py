# -*- coding: utf-8 -*-
"""
Per-city content for the /web-design-<city>-or/ landing pages, EN + ES.

SEO-PLAYBOOK.md section 2 is explicit about the failure mode these pages have
to avoid: "If you swap only the city name into identical copy, Google treats
the pages as doorway pages and can penalize you." So every city gets its own
intro (grounded in real, easily-verifiable civic facts -- county, rivers,
university/capital status -- never invented business history, since we have
none yet in any of these cities) and its own FAQ angle, not a single template
with a find-and-replace.

The one deliberately repeated element is the "are you actually based here"
question -- every city gets it, worded differently. That repetition is
intentional, not a doorway-page tell: this is a real service-area business
with no physical location in any of these cities, and Google's guidance is
that local pages should be honest about that, not paper over it by omission.
"""

CITIES = [
    {
        "slug": "albany",
        "name": "Albany",
        "county": "Linn County",
        "en": {
            "title": "Web Design in Albany, OR | Willamette Web Design",
            "description": ("A complete online presence for Albany, Oregon businesses — "
                            "website, local SEO, Google Business, listings — built in 30 "
                            "days. Bilingual. Free presence check."),
            "h1": "Web Design & Local SEO in Albany, Oregon",
            "lead": ("A complete local presence for Albany businesses — website, "
                    "Google, local SEO, and the systems that turn searches into "
                    "customers — built and connected in 30 days."),
            "intro": [
                ("Albany sits where the Willamette and Calapooia Rivers meet, the "
                 "Linn County seat and a hub for manufacturing, healthcare, and a "
                 "steady base of local retail and trades businesses. A lot of that "
                 "activity now starts with a search on a phone — someone looking "
                 "for a service \"near me\" or by name, deciding in seconds whether "
                 "the result they land on looks trustworthy."),
                ("The Willamette 30-Day Program builds that first impression "
                 "properly: a fast, mobile-first website, a Google Business Profile "
                 "set up or fixed, local listings that match, and a way for the "
                 "leads that come in to actually reach you. Available in English "
                 "and Spanish, for Albany and the surrounding Mid-Willamette "
                 "Valley."),
            ],
            "faq": [
                (
                    "Is Willamette Web Design based in Albany?",
                    "We're a service-area business covering the Mid-Willamette "
                    "Valley, not a storefront in any one city — the whole program "
                    "is designed to run over calls, email, and a couple of video "
                    "check-ins, so where we sit doesn't slow anything down for an "
                    "Albany business.",
                ),
                (
                    "How fast can an Albany business get a new site live?",
                    "30 days from when we have what we need to start: your content, "
                    "any existing accounts, and quick feedback at the review points "
                    "along the way.",
                ),
                (
                    "Do you offer the program in Spanish for Albany clients?",
                    "Sí — the entire program runs in English or Spanish, from the "
                    "first call to the finished site.",
                ),
            ],
        },
        "es": {
            "title": "Diseño Web en Albany, OR | Willamette Web Design",
            "description": ("Presencia en línea completa para negocios de Albany, "
                            "Oregon — sitio web, SEO local, Google Business, directorios "
                            "— en 30 días. Bilingüe. Revisión gratis."),
            "h1": "Diseño Web y SEO Local en Albany, Oregon",
            "lead": ("Una presencia local completa para negocios de Albany — sitio "
                    "web, Google, SEO local y los sistemas que convierten búsquedas "
                    "en clientes — construida y conectada en 30 días."),
            "intro": [
                ("Albany está donde se unen los ríos Willamette y Calapooia, sede "
                 "del condado de Linn y un centro de manufactura, salud, y un grupo "
                 "constante de negocios locales de venta al detalle y oficios. Gran "
                 "parte de esa actividad hoy empieza con una búsqueda desde el "
                 "teléfono — alguien buscando un servicio \"cerca de mí\" o por "
                 "nombre, decidiendo en segundos si el resultado parece confiable."),
                ("El Programa de 30 Días de Willamette construye esa primera "
                 "impresión correctamente: un sitio web rápido y diseñado primero "
                 "para el celular, un Perfil de Negocio de Google configurado o "
                 "corregido, directorios locales consistentes, y una forma real de "
                 "que los clientes potenciales te contacten. Disponible en inglés y "
                 "español, para Albany y el resto del valle medio de Willamette."),
            ],
            "faq": [
                (
                    "¿Willamette Web Design tiene oficina en Albany?",
                    "Somos un negocio de área de servicio que cubre el valle medio "
                    "de Willamette, no una oficina física en una sola ciudad — todo "
                    "el programa está diseñado para funcionar por llamadas, correo y "
                    "un par de videollamadas, así que dónde estemos no retrasa nada "
                    "para un negocio en Albany.",
                ),
                (
                    "¿Qué tan rápido puede un negocio de Albany tener su sitio "
                    "nuevo en línea?",
                    "30 días desde que tenemos lo necesario para empezar: tu "
                    "contenido, cualquier cuenta existente, y retroalimentación "
                    "rápida en los puntos de revisión.",
                ),
                (
                    "¿Ofrecen el programa en español para clientes de Albany?",
                    "Sí — todo el programa funciona en inglés o español, desde la "
                    "primera llamada hasta el sitio terminado.",
                ),
            ],
        },
    },
    {
        "slug": "corvallis",
        "name": "Corvallis",
        "county": "Benton County",
        "en": {
            "title": "Web Design in Corvallis, OR | Willamette Web Design",
            "description": ("A complete online presence for Corvallis, Oregon businesses "
                            "— website, local SEO, Google Business, listings — built "
                            "in 30 days. Bilingual. Free presence check."),
            "h1": "Web Design & Local SEO in Corvallis, Oregon",
            "lead": ("A complete local presence for Corvallis businesses — website, "
                    "Google, local SEO, and the systems that turn searches into "
                    "customers — built and connected in 30 days."),
            "intro": [
                ("Corvallis is the Benton County seat, home to Oregon State "
                 "University and a local economy shaped by it — a customer base "
                 "that's online first, comparison-shops before calling anyone, and "
                 "checks reviews before an appointment. A thin or dated website "
                 "reads as a red flag to that audience faster than it might "
                 "elsewhere."),
                ("The Willamette 30-Day Program gets a Corvallis business a fast, "
                 "mobile-first site, a properly set-up Google Business Profile, "
                 "matching local listings, and a lead-capture path that actually "
                 "works — in 30 days, in English or Spanish."),
            ],
            "faq": [
                (
                    "Is Willamette Web Design based in Corvallis?",
                    "No — we're a service-area business covering the Mid-Willamette "
                    "Valley. The program runs by call, email, and video, so a "
                    "Corvallis business gets the same attention as if we had an "
                    "office downtown.",
                ),
                (
                    "Can you compete with the design quality Corvallis customers "
                    "expect?",
                    "Every site is custom-built and mobile-first, not a stock "
                    "template with your logo swapped in — that's the bar for a "
                    "college-town audience that's used to comparing options online "
                    "before they ever call.",
                ),
                (
                    "Can you replace an existing outdated site?",
                    "Yes. Most of our builds replace an existing site — we rebuild "
                    "it inside the same 30-day program.",
                ),
            ],
        },
        "es": {
            "title": "Diseño Web en Corvallis, OR | Willamette Web Design",
            "description": ("Una presencia en línea completa para negocios de "
                            "Corvallis, Oregon — sitio web, SEO local, Google Business, "
                            "directorios — en 30 días. Bilingüe. Revisión gratis."),
            "h1": "Diseño Web y SEO Local en Corvallis, Oregon",
            "lead": ("Una presencia local completa para negocios de Corvallis — sitio "
                    "web, Google, SEO local y los sistemas que convierten búsquedas "
                    "en clientes — construida y conectada en 30 días."),
            "intro": [
                ("Corvallis es la sede del condado de Benton, hogar de la "
                 "Universidad Estatal de Oregon y una economía local marcada por "
                 "ella — una clientela que busca en línea primero, compara antes "
                 "de llamar, y revisa las reseñas antes de una cita. Un sitio web "
                 "débil o desactualizado se nota como señal de alerta aún más "
                 "rápido con este público."),
                ("El Programa de 30 Días de Willamette le da a un negocio de "
                 "Corvallis un sitio rápido y diseñado primero para el celular, "
                 "un Perfil de Negocio de Google bien configurado, directorios "
                 "locales consistentes, y una vía de contacto que realmente "
                 "funciona — en 30 días, en inglés o español."),
            ],
            "faq": [
                (
                    "¿Willamette Web Design tiene oficina en Corvallis?",
                    "No — somos un negocio de área de servicio que cubre el valle "
                    "medio de Willamette. El programa funciona por llamada, correo "
                    "y video, así que un negocio en Corvallis recibe la misma "
                    "atención que si tuviéramos oficina en el centro.",
                ),
                (
                    "¿Pueden igualar la calidad de diseño que esperan los clientes "
                    "de Corvallis?",
                    "Cada sitio se construye a la medida y primero para el celular, "
                    "no es una plantilla genérica con tu logo — ese es el estándar "
                    "para un público universitario acostumbrado a comparar opciones "
                    "en línea antes de llamar.",
                ),
                (
                    "¿Pueden reemplazar un sitio existente que ya está "
                    "desactualizado?",
                    "Sí. La mayoría de nuestros proyectos reemplazan un sitio "
                    "existente — lo reconstruimos dentro del mismo programa de "
                    "30 días.",
                ),
            ],
        },
    },
    {
        "slug": "salem",
        "name": "Salem",
        "county": "Marion County",
        "en": {
            "title": "Web Design in Salem, OR | Willamette Web Design",
            "description": ("A complete online presence for Salem, Oregon businesses "
                            "— website, local SEO, Google Business, listings — built "
                            "in 30 days. Bilingual. Free presence check."),
            "h1": "Web Design & Local SEO in Salem, Oregon",
            "lead": ("A complete local presence for Salem businesses — website, "
                    "Google, local SEO, and the systems that turn searches into "
                    "customers — built and connected in 30 days."),
            "intro": [
                ("Salem is Oregon's state capital and one of the larger cities in "
                 "the Willamette Valley, with a diverse local economy and a large "
                 "Spanish-speaking community woven through its trades, food "
                 "service, and small-business scene. A website that only speaks to "
                 "half of that customer base is leaving business on the table "
                 "before a single lead ever comes in."),
                ("The Willamette 30-Day Program builds a Salem business a genuinely "
                 "bilingual online presence — site, Google Business Profile, local "
                 "listings, lead capture — not a translated afterthought bolted "
                 "onto an English-only site. Built and connected in 30 days."),
            ],
            "faq": [
                (
                    "Is Willamette Web Design based in Salem?",
                    "No — we're a service-area business covering the Mid-Willamette "
                    "Valley, and the whole program runs over calls, email, and a "
                    "couple of video check-ins, so a Salem business gets full "
                    "attention without needing us to have a local office.",
                ),
                (
                    "Is the Spanish version a real translation, not just Google "
                    "Translate?",
                    "Yes — every page is written in Spanish, not machine-translated, "
                    "and the language switch is a real, separate URL a search "
                    "engine can index on its own, not a script that swaps text.",
                ),
                (
                    "What happens after the first 30 days?",
                    "The $99/month management service takes over: hosting, "
                    "updates, support, monitoring, and continued optimization.",
                ),
            ],
        },
        "es": {
            "title": "Diseño Web en Salem, OR | Willamette Web Design",
            "description": ("Una presencia en línea completa para negocios de Salem, "
                            "Oregon — sitio web, SEO local, Google Business, "
                            "directorios — en 30 días. Bilingüe. Revisión gratis."),
            "h1": "Diseño Web y SEO Local en Salem, Oregon",
            "lead": ("Una presencia local completa para negocios de Salem — sitio "
                    "web, Google, SEO local y los sistemas que convierten búsquedas "
                    "en clientes — construida y conectada en 30 días."),
            "intro": [
                ("Salem es la capital del estado de Oregon y una de las ciudades "
                 "más grandes del valle de Willamette, con una economía local "
                 "diversa y una comunidad de habla hispana grande y presente en "
                 "sus oficios, restaurantes y negocios pequeños. Un sitio web que "
                 "solo le habla a la mitad de esa clientela está dejando negocio "
                 "sobre la mesa antes de que llegue un solo cliente potencial."),
                ("El Programa de 30 Días de Willamette construye para un negocio "
                 "de Salem una presencia en línea genuinamente bilingüe — sitio, "
                 "Perfil de Negocio de Google, directorios locales, captura de "
                 "clientes — no una traducción a medias pegada a un sitio en "
                 "inglés. Construida y conectada en 30 días."),
            ],
            "faq": [
                (
                    "¿Willamette Web Design tiene oficina en Salem?",
                    "No — somos un negocio de área de servicio que cubre el valle "
                    "medio de Willamette, y todo el programa funciona por "
                    "llamadas, correo y videollamadas, así que un negocio en Salem "
                    "recibe atención completa sin que necesitemos oficina local.",
                ),
                (
                    "¿La versión en español es una traducción real, no solo Google "
                    "Translate?",
                    "Sí — cada página está escrita en español, no traducida por "
                    "máquina, y el cambio de idioma es una URL real y separada que "
                    "un buscador puede indexar por su cuenta, no un script que "
                    "cambia el texto.",
                ),
                (
                    "¿Qué pasa después de los primeros 30 días?",
                    "El servicio de gestión de $99/mes toma el control: "
                    "alojamiento, actualizaciones, soporte, monitoreo y "
                    "optimización continua.",
                ),
            ],
        },
    },
    {
        "slug": "lebanon",
        "name": "Lebanon",
        "county": "Linn County",
        "en": {
            "title": "Web Design in Lebanon, OR | Willamette Web Design",
            "description": ("A complete online presence for Lebanon, Oregon businesses "
                            "— website, local SEO, Google Business, listings — built "
                            "in 30 days. Bilingual. Free presence check."),
            "h1": "Web Design & Local SEO in Lebanon, Oregon",
            "lead": ("A complete local presence for Lebanon businesses — website, "
                    "Google, local SEO, and the systems that turn searches into "
                    "customers — built and connected in 30 days."),
            "intro": [
                ("Lebanon is a Linn County town with a farming and timber heritage "
                 "and the close-knit feel of a smaller Willamette Valley "
                 "community, where word of mouth still carries real weight — but "
                 "increasingly starts with someone checking a business's Google "
                 "listing and website before they ever ask a neighbor."),
                ("The Willamette 30-Day Program gives a Lebanon business the same "
                 "complete setup a bigger-city competitor would pay far more for: "
                 "a fast, mobile-first website, a working Google Business "
                 "Profile, matching local listings, and a lead-capture path that "
                 "actually reaches you — in English or Spanish."),
            ],
            "faq": [
                (
                    "Is Willamette Web Design based in Lebanon?",
                    "We're a service-area business covering the Mid-Willamette "
                    "Valley, not a storefront in one town — the program runs by "
                    "call, email, and video, so a Lebanon business gets the same "
                    "attention as anywhere else in the valley.",
                ),
                (
                    "We're a small, family-run business — is the program still a "
                    "fit?",
                    "Yes — the program is built for exactly that size of business: "
                    "one fixed price, one 30-day timeline, and about two hours of "
                    "your time across the month for a kickoff call and quick "
                    "feedback.",
                ),
                (
                    "Do you offer the program in Spanish for Lebanon clients?",
                    "Sí — the entire program runs in English or Spanish, from the "
                    "first call to the finished site.",
                ),
            ],
        },
        "es": {
            "title": "Diseño Web en Lebanon, OR | Willamette Web Design",
            "description": ("Una presencia en línea completa para negocios de "
                            "Lebanon, Oregon — sitio web, SEO local, Google Business, "
                            "directorios — en 30 días. Bilingüe. Revisión gratis."),
            "h1": "Diseño Web y SEO Local en Lebanon, Oregon",
            "lead": ("Una presencia local completa para negocios de Lebanon — sitio "
                    "web, Google, SEO local y los sistemas que convierten búsquedas "
                    "en clientes — construida y conectada en 30 días."),
            "intro": [
                ("Lebanon es un pueblo del condado de Linn con herencia agrícola y "
                 "maderera, y el ambiente cercano de una comunidad más pequeña "
                 "del valle de Willamette, donde el boca a boca todavía pesa — pero "
                 "cada vez más empieza con alguien revisando el listado de Google "
                 "y el sitio web de un negocio antes de preguntarle a un vecino."),
                ("El Programa de 30 Días de Willamette le da a un negocio de "
                 "Lebanon la misma configuración completa que un competidor de "
                 "ciudad grande pagaría mucho más por tener: un sitio web rápido y "
                 "diseñado primero para el celular, un Perfil de Negocio de Google "
                 "funcionando, directorios locales consistentes, y una vía de "
                 "contacto que realmente te llega — en inglés o español."),
            ],
            "faq": [
                (
                    "¿Willamette Web Design tiene oficina en Lebanon?",
                    "Somos un negocio de área de servicio que cubre el valle medio "
                    "de Willamette, no una oficina en un solo pueblo — el programa "
                    "funciona por llamada, correo y video, así que un negocio en "
                    "Lebanon recibe la misma atención que en cualquier otra parte "
                    "del valle.",
                ),
                (
                    "Somos un negocio familiar pequeño — ¿el programa nos sirve?",
                    "Sí — el programa está diseñado exactamente para ese tamaño "
                    "de negocio: un precio fijo, un plazo de 30 días, y como dos "
                    "horas de tu tiempo en el mes para una llamada inicial y "
                    "retroalimentación rápida.",
                ),
                (
                    "¿Ofrecen el programa en español para clientes de Lebanon?",
                    "Sí — todo el programa funciona en inglés o español, desde la "
                    "primera llamada hasta el sitio terminado.",
                ),
            ],
        },
    },
    {
        "slug": "keizer",
        "name": "Keizer",
        "county": "Marion County",
        "en": {
            "title": "Web Design in Keizer, OR | Willamette Web Design",
            "description": ("A complete online presence for Keizer, Oregon businesses — "
                            "website, local SEO, Google Business, listings — built in 30 "
                            "days. Bilingual. Free presence check."),
            "h1": "Web Design & Local SEO in Keizer, Oregon",
            "lead": ("A complete local presence for Keizer businesses — website, "
                    "Google, local SEO, and the systems that turn searches into "
                    "customers — built and connected in 30 days."),
            "intro": [
                ("Keizer is its own incorporated city in Marion County, sitting "
                 "immediately north of Salem along the Willamette River — sharing "
                 "the Salem-Keizer school district and metro area, but with its own "
                 "city government and its own River Road business corridor. A lot "
                 "of search results still lump Keizer in with its bigger neighbor, "
                 "which means a Keizer business can lose the customers searching by "
                 "the name of their own town."),
                ("The Willamette 30-Day Program builds and connects a Keizer "
                 "business's whole local presence — a fast, mobile-first website, a "
                 "Google Business Profile set up to actually surface for Keizer "
                 "searches and not just Salem ones, matching local listings, and a "
                 "lead-capture path that works. Built in 30 days, in English or "
                 "Spanish."),
            ],
            "faq": [
                (
                    "Is Willamette Web Design based in Keizer?",
                    "We're a service-area business covering the Mid-Willamette "
                    "Valley, not a storefront in one city — the program runs by "
                    "call, email, and video, so a Keizer business gets full "
                    "attention without us needing a local office.",
                ),
                (
                    "Most of our customers search for \"Salem\" businesses — does a "
                    "Keizer page even help?",
                    "Yes — we set up your Google Business Profile and site to "
                    "target Keizer specifically as well as the shared Salem-Keizer "
                    "market, so you show up for both instead of disappearing into a "
                    "bigger neighbor's search results.",
                ),
                (
                    "Do you offer the program in Spanish for Keizer clients?",
                    "Sí — the entire program runs in English or Spanish, from the "
                    "first call to the finished site.",
                ),
            ],
        },
        "es": {
            "title": "Diseño Web en Keizer, OR | Willamette Web Design",
            "description": ("Una presencia en línea completa para negocios de Keizer, "
                            "Oregon — sitio web, SEO local, Google Business, directorios "
                            "— en 30 días. Bilingüe. Revisión gratis."),
            "h1": "Diseño Web y SEO Local en Keizer, Oregon",
            "lead": ("Una presencia local completa para negocios de Keizer — sitio "
                    "web, Google, SEO local y los sistemas que convierten búsquedas "
                    "en clientes — construida y conectada en 30 días."),
            "intro": [
                ("Keizer es su propia ciudad incorporada en el condado de Marion, "
                 "justo al norte de Salem junto al río Willamette — comparte el "
                 "distrito escolar Salem-Keizer y el área metropolitana, pero tiene "
                 "su propio gobierno municipal y su propio corredor de negocios en "
                 "River Road. Muchos resultados de búsqueda todavía confunden a "
                 "Keizer con su vecino más grande, lo que significa que un negocio "
                 "de Keizer puede perder a los clientes que buscan por el nombre de "
                 "su propio pueblo."),
                ("El Programa de 30 Días de Willamette construye y conecta toda la "
                 "presencia local de un negocio de Keizer — un sitio web rápido y "
                 "diseñado primero para el celular, un Perfil de Negocio de Google "
                 "configurado para aparecer en búsquedas de Keizer y no solo de "
                 "Salem, directorios locales consistentes, y una vía de contacto "
                 "que funciona. Construido en 30 días, en inglés o español."),
            ],
            "faq": [
                (
                    "¿Willamette Web Design tiene oficina en Keizer?",
                    "Somos un negocio de área de servicio que cubre el valle medio "
                    "de Willamette, no una oficina en una sola ciudad — el programa "
                    "funciona por llamada, correo y video, así que un negocio en "
                    "Keizer recibe atención completa sin que necesitemos oficina "
                    "local.",
                ),
                (
                    "La mayoría de nuestros clientes buscan negocios de \"Salem\" — "
                    "¿de verdad ayuda una página de Keizer?",
                    "Sí — configuramos tu Perfil de Negocio de Google y tu sitio "
                    "para aparecer tanto en búsquedas de Keizer como en el mercado "
                    "compartido de Salem-Keizer, así apareces en ambos en lugar de "
                    "perderte entre los resultados de un vecino más grande.",
                ),
                (
                    "¿Ofrecen el programa en español para clientes de Keizer?",
                    "Sí — todo el programa funciona en inglés o español, desde la "
                    "primera llamada hasta el sitio terminado.",
                ),
            ],
        },
    },
    {
        "slug": "woodburn",
        "name": "Woodburn",
        "county": "Marion County",
        "en": {
            "title": "Web Design in Woodburn, OR | Willamette Web Design",
            "description": ("A complete online presence for Woodburn, Oregon "
                            "businesses — website, local SEO, Google Business, "
                            "listings — built in 30 days. Bilingual. Free presence "
                            "check."),
            "h1": "Web Design & Local SEO in Woodburn, Oregon",
            "lead": ("A complete local presence for Woodburn businesses — website, "
                    "Google, local SEO, and the systems that turn searches into "
                    "customers — built and connected in 30 days."),
            "intro": [
                ("Woodburn sits at the junction of I-5 and Highway 214, roughly "
                 "halfway between Salem and Portland, and has one of the highest "
                 "shares of Latino residents and Spanish speakers of any city in "
                 "Oregon. For a Woodburn business, a Spanish-language site isn't a "
                 "nice-to-have add-on — for a large share of the customer base, "
                 "it's the version of the site that actually gets read."),
                ("The Willamette 30-Day Program builds a genuinely bilingual local "
                 "presence for a Woodburn business — a real Spanish page, not a "
                 "machine translation bolted onto an English site, a Google "
                 "Business Profile and local listings set up correctly in both "
                 "languages, and a lead-capture path that works either way a "
                 "customer searches. Built and connected in 30 days."),
            ],
            "faq": [
                (
                    "Is Willamette Web Design based in Woodburn?",
                    "We're a service-area business covering the Mid-Willamette "
                    "Valley, not a storefront in one city — the program runs by "
                    "call, email, and video, so a Woodburn business gets full "
                    "attention without us needing a local office.",
                ),
                (
                    "Is the Spanish site a real translation, not just Google "
                    "Translate?",
                    "Yes — every page is written in Spanish by a person, not "
                    "machine-translated, and it lives at its own indexable URL, not "
                    "a script that swaps text on the same page.",
                ),
                (
                    "Do you handle both the English and Spanish sides of local "
                    "SEO — Google Business, listings, all of it?",
                    "Yes — Google Business Profile, local listings, and lead "
                    "capture are all set up to work in both languages, not just "
                    "the English side with Spanish bolted on.",
                ),
            ],
        },
        "es": {
            "title": "Diseño Web en Woodburn, OR | Willamette Web Design",
            "description": ("Una presencia en línea completa para negocios de "
                            "Woodburn, Oregon — sitio web, SEO local, Google "
                            "Business, directorios — en 30 días. Bilingüe. Revisión "
                            "gratis."),
            "h1": "Diseño Web y SEO Local en Woodburn, Oregon",
            "lead": ("Una presencia local completa para negocios de Woodburn — "
                    "sitio web, Google, SEO local y los sistemas que convierten "
                    "búsquedas en clientes — construida y conectada en 30 días."),
            "intro": [
                ("Woodburn está en el cruce de la I-5 y la autopista 214, casi a "
                 "medio camino entre Salem y Portland, y tiene una de las "
                 "proporciones más altas de residentes latinos e hispanohablantes "
                 "de cualquier ciudad de Oregon. Para un negocio de Woodburn, un "
                 "sitio en español no es un extra opcional — para gran parte de la "
                 "clientela, es la versión del sitio que realmente se lee."),
                ("El Programa de 30 Días de Willamette construye una presencia "
                 "local genuinamente bilingüe para un negocio de Woodburn — una "
                 "página en español real, no una traducción automática pegada a un "
                 "sitio en inglés, un Perfil de Negocio de Google y directorios "
                 "locales bien configurados en ambos idiomas, y una vía de contacto "
                 "que funciona sin importar en qué idioma busque el cliente. "
                 "Construida y conectada en 30 días."),
            ],
            "faq": [
                (
                    "¿Willamette Web Design tiene oficina en Woodburn?",
                    "Somos un negocio de área de servicio que cubre el valle medio "
                    "de Willamette, no una oficina en una sola ciudad — el programa "
                    "funciona por llamada, correo y video, así que un negocio en "
                    "Woodburn recibe atención completa sin que necesitemos oficina "
                    "local.",
                ),
                (
                    "¿El sitio en español es una traducción real, no solo Google "
                    "Translate?",
                    "Sí — cada página está escrita en español por una persona, no "
                    "traducida por máquina, y vive en su propia URL indexable, no "
                    "en un script que cambia el texto en la misma página.",
                ),
                (
                    "¿Manejan el SEO local tanto en inglés como en español — "
                    "Google Business, directorios, todo?",
                    "Sí — el Perfil de Negocio de Google, los directorios locales "
                    "y la captura de clientes están configurados para funcionar en "
                    "ambos idiomas, no solo en inglés con español añadido después.",
                ),
            ],
        },
    },
]
