# -*- coding: utf-8 -*-
"""
Content for the Privacy Policy and Terms of Service, EN + ES.

IMPORTANT — this is a working draft, not legal advice. It is written to be
accurate about what this specific site actually does (a free-audit form, a
deferred analytics tag, static hosting) rather than being generic boilerplate,
because a privacy policy that describes data collection you do not do is both
useless and misleading.

Anything that depends on the signed client agreement is marked with
NEEDS_REVIEW and rendered as a visible callout. Those are business and legal
decisions, and inventing them would put wrong terms in front of customers.
"""

REVIEW = "NEEDS_REVIEW"

PRIVACY = {
    "en": {
        "title": "Privacy Policy | Willamette Web Design",
        "description": ("How Willamette Web Design collects, uses and protects your "
                        "information, including the free website audit form and analytics."),
        "h1": "Privacy Policy",
        "updated": "Last updated: {date}",
        "intro": ("This policy explains what information Willamette Web Design collects "
                  "when you use willametteweb.com, why we collect it, and what choices "
                  "you have. We have written it to describe what this site actually "
                  "does — nothing more."),
        "sections": [
            ("Who we are", [
                ("p", "Willamette Web Design is a web design and local marketing business "
                      "serving the Willamette Valley, Oregon."),
                ("contact", None),
            ]),
            ("What we collect", [
                ("p", "We collect only two kinds of information."),
                ("h3", "1. Information you give us"),
                ("p", "When you submit the free website audit form, we collect your "
                      "business name, your website address, and your email address. "
                      "If you apply for the 30-Day Program, we collect the business "
                      "and contact details you enter in that form."),
                ("p", "You choose what to send us. We do not require an account, and "
                      "we do not ask for payment details through this website."),
                ("h3", "2. Information collected automatically"),
                ("p", "Our host records standard server logs (IP address, browser type, "
                      "pages requested, timestamps) for security and reliability."),
                ("p", "If website analytics are enabled, we use Google Analytics 4 to "
                      "understand how visitors find and move through the site. The "
                      "analytics script is deliberately loaded late, only after you "
                      "interact with the page or a few seconds have passed, so it never "
                      "slows your first view of the site. Analytics data is aggregated "
                      "and is not used to identify you personally."),
            ]),
            ("How we use your information", [
                ("ul", [
                    "To prepare and send the free website audit you requested.",
                    "To respond to your enquiry or application.",
                    "To follow up about our services, if you contacted us about them.",
                    "To understand which pages are useful and improve the site.",
                    "To keep the site secure and working.",
                ]),
                ("p", "Every marketing email we send includes an unsubscribe link. "
                      "Unsubscribing stops marketing email; we may still reply to a "
                      "question you asked us directly."),
                ("p", "We do not sell your personal information. We do not share it "
                      "with advertisers, and we do not use it for cross-site "
                      "advertising."),
            ]),
            ("Who we share it with", [
                ("p", "We share information only with the service providers that make "
                      "this business run, and only so they can perform that service:"),
                ("ul", [
                    "Our website host, which serves this site and keeps server logs.",
                    "Our email provider, which delivers and stores our correspondence.",
                    "Google Analytics, if analytics are enabled, for aggregated traffic reporting.",
                ]),
                ("p", "We may also disclose information if the law requires it, or to "
                      "protect our rights or someone's safety."),
            ]),
            ("Cookies", [
                ("p", "This site sets no advertising cookies and runs no ad trackers."),
                ("p", "If analytics are enabled, Google Analytics sets cookies to tell "
                      "returning visits from new ones. You can block or delete cookies "
                      "in your browser settings, and the site will continue to work "
                      "normally. Browsers that send a Global Privacy Control signal are "
                      "honoured as an opt-out request."),
            ]),
            ("How long we keep it", [
                ("p", "Audit requests and enquiries are kept for as long as we are in "
                      "contact with you and for a reasonable period afterwards, so we "
                      "have a record of what we discussed. Client project records are "
                      "kept for as long as we need them for accounting and legal "
                      "purposes. You can ask us to delete your information at any time."),
            ]),
            ("Your choices and rights", [
                ("p", "You can ask us to:"),
                ("ul", [
                    "Tell you what personal information we hold about you.",
                    "Correct anything that is wrong.",
                    "Delete your information.",
                    "Stop sending you marketing email.",
                ]),
                ("p", "Email us at {email} and we will respond. Depending on where you "
                      "live — for example under the Oregon Consumer Privacy Act or "
                      "California law — you may have additional rights. We extend "
                      "the choices above to everyone who asks, regardless of whether a "
                      "particular law applies to us."),
                ("p", "We will not discriminate against you for exercising any of these "
                      "rights."),
            ]),
            ("Children", [
                ("p", "This site is intended for businesses and is not directed at "
                      "children under 13. We do not knowingly collect information from "
                      "children."),
            ]),
            ("Security", [
                ("p", "The site is served over HTTPS. We limit who can access enquiry "
                      "data to the people who need it. No method of transmission or "
                      "storage is completely secure, so we cannot promise absolute "
                      "security."),
            ]),
            ("Changes to this policy", [
                ("p", "If we change how we handle information, we will update this page "
                      "and change the date at the top."),
            ]),
            ("Contact us", [
                ("p", "Questions about this policy, or a request about your information:"),
                ("contact", None),
            ]),
        ],
    },
}

TERMS = {
    "en": {
        "title": "Terms of Service | Willamette Web Design",
        "description": ("Terms for the Willamette 30-Day Program and ongoing "
                        "management: what's included, pricing, the 30-day satisfaction "
                        "guarantee, and ownership."),
        "h1": "Terms of Service",
        "updated": "Last updated: {date}",
        "intro": ("These terms apply when you use this website or buy services from "
                  "Willamette Web Design. Please read them before applying for the "
                  "30-Day Program."),
        "sections": [
            ("Agreement", [
                ("p", "By using this site or purchasing our services, you agree to these "
                      "terms. If you do not agree, please do not use the site or buy "
                      "the services."),
                ("p", "Where a signed proposal or service agreement covers the same "
                      "subject as these terms, that signed agreement controls."),
            ]),
            ("What we provide", [
                ("p", "The Willamette 30-Day Program is a fixed-scope engagement to "
                      "build a business website and set up the surrounding local "
                      "presence. Depending on your scope, that can include:"),
                ("ul", [
                    "A custom, responsive business website.",
                    "Local SEO foundations — titles, metadata, on-page structure.",
                    "Google Business Profile setup or optimization.",
                    "Local listings and citations.",
                    "Social profile setup.",
                    "Lead capture forms and call pathways.",
                    "Analytics and conversion tracking.",
                ]),
                ("p", "The exact deliverables for your project are the ones written in "
                      "your proposal."),
                ("review", "Confirm this list against the final approved scope, and "
                           "state explicitly which items are included at the base price "
                           "versus quoted separately."),
            ]),
            ("Pricing and payment", [
                ("p", "The 30-Day Program is $799, charged once. Ongoing management is "
                      "$99 per month."),
                ("review", "Confirm and state plainly: (1) when the $99/month begins "
                           "and how it is billed; (2) whether ongoing management is "
                           "optional or required; (3) the notice period to cancel; "
                           "(4) any third-party or hard costs the client pays directly "
                           "— domain registration, premium plugins, paid directory "
                           "listings, stock imagery — and whether those are "
                           "refundable. Material terms must be disclosed before "
                           "purchase, not after."),
            ]),
            ("30-day money-back satisfaction guarantee", [
                ("p", "If you are not satisfied with the work, you may request a refund "
                      "of the program fee within 30 days."),
                ("review", "This section must match the signed agreement word for word "
                           "before launch. It needs to state: the date the 30 days start "
                           "from; how to make a request; what is refunded and what is "
                           "not (particularly non-recoverable third-party costs); and "
                           "what happens to the website, domain and accounts after a "
                           "refund. A guarantee that is vague about these points causes "
                           "disputes."),
            ]),
            ("What we need from you", [
                ("p", "To deliver in 30 days we need you to provide content, images, "
                      "and access to any existing accounts, and to respond to questions "
                      "and review requests in good time. The 30-day timeline runs from "
                      "when we have what we need to start."),
                ("p", "You confirm that any content, images, or logos you give us are "
                      "yours to use, or that you have permission to use them."),
            ]),
            ("Ownership", [
                ("p", "Your business content, your domain and your brand assets remain "
                      "yours throughout."),
                ("review", "State clearly who owns the finished website files and "
                           "design after final payment, and what happens to hosting and "
                           "accounts if the ongoing management service ends. \"Do I own "
                           "my website?\" is one of the FAQ questions on the homepage, "
                           "and the answer here must match the answer there."),
            ]),
            ("Results", [
                ("p", "We build sites to be fast, accessible, and structured to rank "
                      "well, and we follow current best practice for local search. We "
                      "cannot control Google's ranking systems, competitors, or how "
                      "much demand exists in your market."),
                ("p", "We therefore do not guarantee specific rankings, traffic volumes, "
                      "lead counts, or revenue. Any figures we discuss are illustrative "
                      "and are not a promise of results. Our guarantee is about your "
                      "satisfaction with our work, not about a business outcome."),
            ]),
            ("Third-party services", [
                ("p", "Your site may rely on services we do not control — hosting, "
                      "domain registration, Google Business Profile, email delivery, "
                      "analytics. Those services have their own terms, and we are not "
                      "responsible for their availability, changes, or policies."),
            ]),
            ("Limitation of liability", [
                ("p", "To the extent the law allows, Willamette Web Design is not liable "
                      "for indirect, incidental, or consequential damages, including "
                      "lost profits or lost business. Our total liability for any claim "
                      "is limited to the amount you paid us for the service the claim "
                      "relates to."),
                ("p", "Nothing in these terms limits liability that cannot be limited by "
                      "law."),
            ]),
            ("Ending the engagement", [
                ("p", "Either of us may end an ongoing monthly service with reasonable "
                      "notice. Work already completed remains payable."),
                ("review", "Set the notice period, and state what the client receives "
                           "on exit — file export, domain transfer, account access."),
            ]),
            ("Governing law", [
                ("p", "These terms are governed by the laws of the State of Oregon, "
                      "United States, and any dispute will be handled in the courts of "
                      "Oregon."),
            ]),
            ("Changes", [
                ("p", "We may update these terms. The version published on this page at "
                      "the time you buy is the version that applies to your purchase."),
            ]),
            ("Contact", [
                ("p", "Questions about these terms:"),
                ("contact", None),
            ]),
        ],
    },
}


# --- Spanish -----------------------------------------------------------------
# Translated, not machine-swapped: the same meaning in natural Spanish. The
# bilingual promise is a core differentiator, so a clumsy Spanish legal page
# would undercut the positioning.

PRIVACY["es"] = {
    "title": "Política de Privacidad | Willamette Web Design",
    "description": ("Cómo Willamette Web Design recopila, usa y protege tu información, "
                    "incluyendo el formulario de auditoría gratuita y las analíticas."),
    "h1": "Política de Privacidad",
    "updated": "Última actualización: {date}",
    "intro": ("Esta política explica qué información recopila Willamette Web Design "
              "cuando usas willametteweb.com, por qué la recopilamos y qué opciones "
              "tienes. La escribimos para describir lo que este sitio realmente hace — "
              "nada más."),
    "sections": [
        ("Quiénes somos", [
            ("p", "Willamette Web Design es un negocio de diseño web y marketing local "
                  "que atiende al valle de Willamette, Oregon."),
            ("contact", None),
        ]),
        ("Qué recopilamos", [
            ("p", "Solo recopilamos dos tipos de información."),
            ("h3", "1. Información que nos das"),
            ("p", "Cuando envías el formulario de auditoría gratuita, recopilamos el "
                  "nombre de tu negocio, la dirección de tu sitio web y tu correo "
                  "electrónico. Si aplicas al Programa de 30 Días, recopilamos los "
                  "datos del negocio y de contacto que escribas en ese formulario."),
            ("p", "Tú decides qué enviarnos. No necesitas crear una cuenta y no pedimos "
                  "datos de pago a través de este sitio."),
            ("h3", "2. Información recopilada automáticamente"),
            ("p", "Nuestro proveedor de alojamiento guarda registros estándar del "
                  "servidor (dirección IP, tipo de navegador, páginas solicitadas, "
                  "fecha y hora) por seguridad y estabilidad."),
            ("p", "Si las analíticas están activadas, usamos Google Analytics 4 para "
                  "entender cómo los visitantes encuentran y recorren el sitio. El "
                  "script se carga tarde a propósito, solo después de que interactúas "
                  "con la página o pasan unos segundos, para que nunca retrase lo que "
                  "ves primero. Los datos son agregados y no se usan para "
                  "identificarte personalmente."),
        ]),
        ("Cómo usamos tu información", [
            ("ul", [
                "Para preparar y enviarte la auditoría gratuita que pediste.",
                "Para responder a tu consulta o solicitud.",
                "Para dar seguimiento sobre nuestros servicios, si nos contactaste por ellos.",
                "Para entender qué páginas son útiles y mejorar el sitio.",
                "Para mantener el sitio seguro y funcionando.",
            ]),
            ("p", "Cada correo de marketing que enviamos incluye un enlace para darte "
                  "de baja. Darte de baja detiene el correo de marketing; aún podemos "
                  "responder a una pregunta que nos hiciste directamente."),
            ("p", "No vendemos tu información personal. No la compartimos con "
                  "anunciantes y no la usamos para publicidad entre sitios."),
        ]),
        ("Con quién la compartimos", [
            ("p", "Solo compartimos información con los proveedores que hacen funcionar "
                  "este negocio, y únicamente para que presten ese servicio:"),
            ("ul", [
                "Nuestro proveedor de alojamiento, que sirve este sitio y guarda registros.",
                "Nuestro proveedor de correo, que entrega y almacena nuestra correspondencia.",
                "Google Analytics, si está activado, para reportes de tráfico agregados.",
            ]),
            ("p", "También podemos divulgar información si la ley lo exige, o para "
                  "proteger nuestros derechos o la seguridad de alguien."),
        ]),
        ("Cookies", [
            ("p", "Este sitio no coloca cookies de publicidad ni ejecuta rastreadores "
                  "de anuncios."),
            ("p", "Si las analíticas están activadas, Google Analytics coloca cookies "
                  "para distinguir visitas nuevas de visitas que regresan. Puedes "
                  "bloquear o borrar cookies en tu navegador y el sitio seguirá "
                  "funcionando con normalidad. Respetamos la señal Global Privacy "
                  "Control como una solicitud de exclusión."),
        ]),
        ("Cuánto tiempo la guardamos", [
            ("p", "Guardamos las solicitudes de auditoría y las consultas mientras "
                  "estemos en contacto contigo y por un tiempo razonable después, para "
                  "tener registro de lo que hablamos. Los expedientes de clientes se "
                  "conservan el tiempo necesario por razones contables y legales. "
                  "Puedes pedirnos que borremos tu información cuando quieras."),
        ]),
        ("Tus opciones y derechos", [
            ("p", "Puedes pedirnos que:"),
            ("ul", [
                "Te digamos qué información personal tenemos sobre ti.",
                "Corrijamos cualquier dato incorrecto.",
                "Borremos tu información.",
                "Dejemos de enviarte correo de marketing.",
            ]),
            ("p", "Escríbenos a {email} y te responderemos. Según dónde vivas — por "
                  "ejemplo bajo la Ley de Privacidad del Consumidor de Oregon o la ley "
                  "de California — puedes tener derechos adicionales. Ofrecemos las "
                  "opciones anteriores a cualquier persona que las solicite, aplique o "
                  "no esa ley en nuestro caso."),
            ("p", "No te trataremos de forma diferente por ejercer estos derechos."),
        ]),
        ("Menores", [
            ("p", "Este sitio está dirigido a negocios y no a menores de 13 años. No "
                  "recopilamos información de menores a sabiendas."),
        ]),
        ("Seguridad", [
            ("p", "El sitio se sirve por HTTPS. Limitamos quién puede acceder a los "
                  "datos de las consultas a las personas que lo necesitan. Ningún "
                  "método de transmisión o almacenamiento es completamente seguro, así "
                  "que no podemos prometer seguridad absoluta."),
        ]),
        ("Cambios a esta política", [
            ("p", "Si cambiamos la forma en que manejamos la información, actualizaremos "
                  "esta página y la fecha que aparece arriba."),
        ]),
        ("Contáctanos", [
            ("p", "¿Preguntas sobre esta política o una solicitud sobre tu información?"),
            ("contact", None),
        ]),
    ],
}

TERMS["es"] = {
    "title": "Términos del Servicio | Willamette Web Design",
    "description": ("Los términos que aplican al Programa de 30 Días de Willamette, "
                    "la gestión mensual y el uso de willametteweb.com."),
    "h1": "Términos del Servicio",
    "updated": "Última actualización: {date}",
    "intro": ("Estos términos aplican cuando usas este sitio o contratas servicios de "
              "Willamette Web Design. Por favor léelos antes de aplicar al Programa de "
              "30 Días."),
    "sections": [
        ("Aceptación", [
            ("p", "Al usar este sitio o contratar nuestros servicios, aceptas estos "
                  "términos. Si no estás de acuerdo, por favor no uses el sitio ni "
                  "contrates los servicios."),
            ("p", "Cuando una propuesta o contrato firmado cubra el mismo tema que "
                  "estos términos, el contrato firmado tiene prioridad."),
        ]),
        ("Qué ofrecemos", [
            ("p", "El Programa de 30 Días de Willamette es un trabajo de alcance fijo "
                  "para construir el sitio web de un negocio y configurar su presencia "
                  "local. Según tu alcance, puede incluir:"),
            ("ul", [
                "Un sitio web personalizado y responsivo.",
                "Bases de SEO local — títulos, metadatos, estructura de página.",
                "Configuración u optimización del Perfil de Negocio de Google.",
                "Directorios y citaciones locales.",
                "Configuración de perfiles sociales.",
                "Formularios de captura de clientes y vías de contacto telefónico.",
                "Analíticas y seguimiento de conversiones.",
            ]),
            ("p", "Los entregables exactos de tu proyecto son los que estén escritos en "
                  "tu propuesta."),
            ("review", "Confirmar esta lista contra el alcance final aprobado, y decir "
                       "explícitamente qué se incluye en el precio base y qué se cotiza "
                       "aparte."),
        ]),
        ("Precios y pago", [
            ("p", "El Programa de 30 Días cuesta $799, cobrados una sola vez. La "
                  "gestión mensual cuesta $99 al mes."),
            ("review", "Confirmar y declarar con claridad: (1) cuándo empieza el cobro "
                       "de $99/mes y cómo se factura; (2) si la gestión mensual es "
                       "opcional u obligatoria; (3) el aviso necesario para cancelar; "
                       "(4) qué costos de terceros paga el cliente directamente — "
                       "dominio, plugins de pago, directorios pagados, imágenes de "
                       "stock — y si son reembolsables. Los términos materiales deben "
                       "revelarse antes de la compra, no después."),
        ]),
        ("Garantía de satisfacción de 30 días", [
            ("p", "Si no quedas satisfecho con el trabajo, puedes solicitar un reembolso "
                  "de la tarifa del programa dentro de los 30 días."),
            ("review", "Esta sección debe coincidir palabra por palabra con el contrato "
                       "firmado antes del lanzamiento. Debe indicar: desde qué fecha "
                       "corren los 30 días; cómo hacer la solicitud; qué se reembolsa y "
                       "qué no (en particular costos de terceros no recuperables); y "
                       "qué pasa con el sitio, el dominio y las cuentas después de un "
                       "reembolso."),
        ]),
        ("Qué necesitamos de ti", [
            ("p", "Para entregar en 30 días necesitamos que nos proporciones contenido, "
                  "imágenes y acceso a cuentas existentes, y que respondas a preguntas y "
                  "revisiones a tiempo. El plazo de 30 días corre desde que tenemos lo "
                  "necesario para empezar."),
            ("p", "Confirmas que el contenido, las imágenes o los logotipos que nos des "
                  "son tuyos o que tienes permiso para usarlos."),
        ]),
        ("Propiedad", [
            ("p", "El contenido de tu negocio, tu dominio y los elementos de tu marca "
                  "siguen siendo tuyos en todo momento."),
            ("review", "Indicar con claridad quién es dueño de los archivos y el diseño "
                       "del sitio terminado tras el pago final, y qué pasa con el "
                       "alojamiento y las cuentas si termina la gestión mensual. "
                       "\"¿Soy dueño de mi sitio web?\" es una de las preguntas del FAQ "
                       "en la página principal y la respuesta debe coincidir."),
        ]),
        ("Resultados", [
            ("p", "Construimos sitios rápidos, accesibles y estructurados para "
                  "posicionar bien, y seguimos las mejores prácticas actuales de "
                  "búsqueda local. No controlamos los sistemas de clasificación de "
                  "Google, a la competencia, ni cuánta demanda existe en tu mercado."),
            ("p", "Por eso no garantizamos posiciones específicas, volumen de tráfico, "
                  "número de clientes potenciales ni ingresos. Cualquier cifra que "
                  "mencionemos es ilustrativa y no es una promesa de resultados. "
                  "Nuestra garantía es sobre tu satisfacción con nuestro trabajo, no "
                  "sobre un resultado comercial."),
        ]),
        ("Servicios de terceros", [
            ("p", "Tu sitio puede depender de servicios que no controlamos — "
                  "alojamiento, registro de dominio, Perfil de Negocio de Google, envío "
                  "de correo, analíticas. Esos servicios tienen sus propios términos y "
                  "no somos responsables de su disponibilidad, cambios o políticas."),
        ]),
        ("Limitación de responsabilidad", [
            ("p", "En la medida que la ley lo permita, Willamette Web Design no es "
                  "responsable de daños indirectos, incidentales o consecuentes, "
                  "incluyendo pérdida de ganancias o de negocio. Nuestra "
                  "responsabilidad total por cualquier reclamo se limita al monto que "
                  "nos pagaste por el servicio relacionado con ese reclamo."),
            ("p", "Nada en estos términos limita la responsabilidad que no puede "
                  "limitarse por ley."),
        ]),
        ("Terminación", [
            ("p", "Cualquiera de las partes puede terminar un servicio mensual con "
                  "aviso razonable. El trabajo ya realizado sigue siendo pagadero."),
            ("review", "Definir el periodo de aviso y qué recibe el cliente al salir — "
                       "exportación de archivos, transferencia de dominio, acceso a "
                       "cuentas."),
        ]),
        ("Ley aplicable", [
            ("p", "Estos términos se rigen por las leyes del Estado de Oregon, Estados "
                  "Unidos, y cualquier disputa se resolverá en los tribunales de "
                  "Oregon."),
        ]),
        ("Cambios", [
            ("p", "Podemos actualizar estos términos. La versión publicada en esta "
                  "página al momento de tu compra es la que aplica a esa compra."),
        ]),
        ("Contacto", [
            ("p", "¿Preguntas sobre estos términos?"),
            ("contact", None),
        ]),
    ],
}
