"""
Copy and field definitions for the 30-Day Program application (EN + ES).

Read by scripts/build-apply.py, which turns this into /apply/, /es/apply/ and
the two confirmation pages.

TWO RULES THIS FILE EXISTS TO ENFORCE
-------------------------------------
1. **Field names are canonical and identical across languages.** A field's
   `name` is a database column, not UI text. Deriving names from translated
   labels would send two different shapes to one table and mangle accents --
   see CLAUDE.md, "Forms". Translate `label`, never `name`.

2. **The application is a different flow from the free presence check.** The
   presence check is the soft conversion for people who are not ready; this is
   the primary one. Nothing here calls itself an "audit" (CLAUDE.md).

Nothing in this copy claims anything unverifiable: no client counts, no
testimonials, no "only N spots left". The capacity line is the blueprint's own
approved wording, which is true on any day it is read.
"""

# ---------------------------------------------------------------------------
# Page-level copy
# ---------------------------------------------------------------------------

PAGE = {
    "en": {
        "title": "Apply for the 30-Day Program | Willamette Web Design",
        "description": (
            "Apply for the Willamette 30-Day Program: a complete local presence "
            "— website, Google, local SEO and lead capture — for $799. English "
            "and Español."
        ),
        "eyebrow": "THE WILLAMETTE 30-DAY PROGRAM",
        "h1": "Apply for the 30-Day Program",
        "lead": (
            "We take on a limited number of new businesses each month, and we read "
            "every application ourselves. Tell us about your business and we'll give "
            "you a straight answer on whether the program is the right fit — and what "
            "your 30 days would look like."
        ),
        "terms_line": (
            "$799 one-time  ·  then $99/month for ongoing management  ·  "
            "30-day money-back satisfaction guarantee"
        ),
        "time_line": (
            "Takes about two minutes. The first step is just your contact details, so "
            "if you have to stop there we can still reach you."
        ),
        "aside_steps_heading": "What happens after you apply",
        "aside_steps": [
            "We read it ourselves — no automated screening, no sales sequence.",
            "We reply within one business day with a straight answer on fit and the "
            "next available start date.",
            "If it's a good fit, we set up a short call to plan your 30 days.",
        ],
        "aside_talk_heading": "Rather talk first?",
        "aside_talk": "Call or email us — English or Español, either way.",
        "aside_check_heading": "Not ready to apply?",
        "aside_check": "Get a free presence check instead — no commitment, and the "
                       "written report is yours to keep.",
        "aside_check_cta": "Get a free presence check",
        "submit": "Submit my application",
        "next": "Continue",
        "back": "Back",
        "step_of": "Step {n} of {total}",
        "sending": "Sending…",
        "error": ("Something went wrong. Please call (541) 497-9531 or email "
                  "info@willametteweb.com and we'll take your application over the phone."),
        "honeypot": "Leave this field empty",
        "msg_required": "Please fill in the fields marked with an asterisk.",
        "msg_contact": "We need either a phone number or an email — otherwise we have no way to reach you.",
        "msg_invalid": "That doesn't look quite right. Please check the highlighted field.",
        "form_heading": "Your application",
    },
    "es": {
        "title": "Aplica al Programa de 30 Días | Willamette Web Design",
        "description": (
            "Aplica al Programa de 30 Días: sitio web, Google, SEO local y captación "
            "de clientes por $799. Todo el proceso disponible en español. Respondemos "
            "en un día hábil."
        ),
        "eyebrow": "EL PROGRAMA DE 30 DÍAS",
        "h1": "Aplica al Programa de 30 Días",
        "lead": (
            "Aceptamos un número limitado de negocios nuevos cada mes, y leemos cada "
            "solicitud nosotros mismos. Cuéntanos de tu negocio y te diremos con "
            "franqueza si el programa es lo correcto para ti — y cómo serían tus 30 días."
        ),
        "terms_line": (
            "$799 pago único  ·  luego $99/mes de gestión continua  ·  "
            "garantía de satisfacción de 30 días con devolución de dinero"
        ),
        "time_line": (
            "Toma unos dos minutos. El primer paso son solo tus datos de contacto, así "
            "que si tienes que detenerte ahí, todavía podemos comunicarnos contigo."
        ),
        "aside_steps_heading": "Qué pasa después de aplicar",
        "aside_steps": [
            "La leemos nosotros mismos — sin filtros automáticos ni secuencias de venta.",
            "Respondemos en un día hábil con una respuesta clara sobre si encaja y la "
            "próxima fecha de inicio disponible.",
            "Si encaja, coordinamos una llamada corta para planear tus 30 días.",
        ],
        "aside_talk_heading": "¿Prefieres hablar primero?",
        "aside_talk": "Llámanos o escríbenos — en español o en inglés.",
        "aside_check_heading": "¿Aún no estás listo para aplicar?",
        "aside_check": "Pide una revisión de presencia gratis — sin compromiso, y el "
                       "reporte escrito es tuyo.",
        "aside_check_cta": "Obtén una revisión de presencia gratis",
        "submit": "Enviar mi solicitud",
        "next": "Continuar",
        "back": "Atrás",
        "step_of": "Paso {n} de {total}",
        "sending": "Enviando…",
        "error": ("Algo salió mal. Llámanos al (541) 497-9531 o escribe a "
                  "info@willametteweb.com y tomamos tu solicitud por teléfono."),
        "honeypot": "Deja este campo vacío",
        "msg_required": "Completa los campos marcados con asterisco.",
        "msg_contact": "Necesitamos un teléfono o un correo — si no, no tenemos cómo contactarte.",
        "msg_invalid": "Eso no se ve bien. Revisa el campo marcado.",
        "form_heading": "Tu solicitud",
    },
}

# ---------------------------------------------------------------------------
# Confirmation page
# ---------------------------------------------------------------------------

THANKS = {
    "en": {
        "title": "Application received | Willamette Web Design",
        "description": (
            "Your application for the Willamette 30-Day Program is in. We read every "
            "application by hand and reply within one business day."
        ),
        "h1": "Your application is in.",
        "lead": (
            "We read every application by hand and get back to you within one business "
            "day — with a straight answer on fit, and the next available start date."
        ),
        "steps_heading": "What happens next",
        "steps": [
            ("Check your inbox.", "If you gave us an email, our reply comes from "
                                  "info@willametteweb.com. Worth adding to your contacts "
                                  "so it doesn't land in spam."),
            ("We'll tell you straight.", "If the 30-Day Program isn't the right fit for "
                                         "your business, we'll say so and point you at what is."),
            ("Nothing to pay yet.", "Applying costs nothing and commits you to nothing."),
        ],
        "call_line": "Need to reach us sooner? Call {phone} — English or Español.",
        "booking_heading": "Want to lock in a time now?",
        "booking_cta": "Book a call",
        "home_cta": "Back to the homepage",
    },
    "es": {
        "title": "Solicitud recibida | Willamette Web Design",
        "description": (
            "Tu solicitud para el Programa de 30 Días fue recibida. Leemos cada "
            "solicitud a mano y respondemos en un día hábil."
        ),
        "h1": "Recibimos tu solicitud.",
        "lead": (
            "Leemos cada solicitud nosotros mismos y te respondemos en un día hábil — "
            "con una respuesta clara sobre si encaja y la próxima fecha de inicio."
        ),
        "steps_heading": "Qué sigue",
        "steps": [
            ("Revisa tu correo.", "Si nos diste un correo, nuestra respuesta llega de "
                                  "info@willametteweb.com. Agrégalo a tus contactos para "
                                  "que no caiga en spam."),
            ("Te diremos la verdad.", "Si el Programa de 30 Días no es lo correcto para "
                                      "tu negocio, te lo decimos y te orientamos hacia lo que sí lo es."),
            ("Todavía no hay nada que pagar.", "Aplicar no cuesta nada y no te compromete a nada."),
        ],
        "call_line": "¿Necesitas hablar antes? Llama al {phone} — en español o en inglés.",
        "booking_heading": "¿Quieres apartar una hora ahora?",
        "booking_cta": "Agenda una llamada",
        "home_cta": "Volver al inicio",
    },
}

# ---------------------------------------------------------------------------
# The four steps
#
# `name` is the database column and is NEVER translated. Field order here is
# the order on the page, which is the order of commitment: contact first, then
# qualifying detail. See docs/FUNNEL-BLUEPRINT.md.
# ---------------------------------------------------------------------------

STEPS = [
    {
        "id": "contact",
        "legend": {"en": "How to reach you", "es": "Cómo contactarte"},
        "note": {
            "en": "Just this much to start. If you stop here, this is already enough "
                  "for us to get back to you.",
            "es": "Solo esto para empezar. Si te detienes aquí, ya es suficiente para "
                  "que podamos responderte.",
        },
        "two_up": True,
        "fields": [
            {
                "name": "name", "type": "text", "required": True, "autocomplete": "name",
                "label": {"en": "Your name", "es": "Tu nombre"},
                "placeholder": {"en": "Maria Ramirez", "es": "María Ramírez"},
            },
            {
                "name": "business_name", "type": "text", "required": True,
                "autocomplete": "organization",
                "label": {"en": "Business name", "es": "Nombre del negocio"},
                "placeholder": {"en": "Ramirez Roofing", "es": "Techos Ramírez"},
            },
            {
                "name": "email", "type": "email", "autocomplete": "email",
                "label": {"en": "Email", "es": "Correo electrónico"},
                "placeholder": {"en": "you@example.com", "es": "tu@ejemplo.com"},
                "hint": {
                    "en": "Email or phone — whichever you'd rather we used.",
                    "es": "Correo o teléfono — el que prefieras que usemos.",
                },
            },
            {
                "name": "phone", "type": "tel", "autocomplete": "tel",
                "label": {"en": "Phone", "es": "Teléfono"},
                "placeholder": {"en": "(541) 555-0134", "es": "(541) 555-0134"},
                "hint": {
                    "en": "We need at least one of these two.",
                    "es": "Necesitamos al menos uno de los dos.",
                },
            },
        ],
    },
    {
        "id": "presence",
        "legend": {"en": "Your business today", "es": "Tu negocio hoy"},
        "note": {
            "en": "So we can look at what you already have before we talk.",
            "es": "Para poder ver lo que ya tienes antes de hablar contigo.",
        },
        "two_up": True,
        "fields": [
            {
                "name": "industry", "type": "text",
                "label": {"en": "What kind of work do you do?",
                          "es": "¿A qué se dedica tu negocio?"},
                "placeholder": {"en": "Roofing, dental, landscaping…",
                                "es": "Techos, dental, jardinería…"},
            },
            {
                "name": "service_area", "type": "text",
                "label": {"en": "City or area you serve",
                          "es": "Ciudad o área que atiendes"},
                "placeholder": {"en": "Albany and Linn County",
                                "es": "Albany y el condado de Linn"},
            },
            {
                "name": "website_url", "type": "text", "autocomplete": "url",
                "span": True,
                "label": {"en": "Current website", "es": "Sitio web actual"},
                "placeholder": {"en": "yourbusiness.com — or leave blank if you don't have one",
                                "es": "tunegocio.com — o déjalo vacío si no tienes"},
            },
            {
                "name": "has_gbp", "type": "radio", "span": True,
                "label": {"en": "Do you have a Google Business Profile?",
                          "es": "¿Tienes un Perfil de Empresa en Google?"},
                "hint": {
                    "en": "The listing with your map pin, hours and reviews. Not having "
                          "one is fine — setting it up is part of the program.",
                    "es": "El listado con tu mapa, horario y reseñas. No tenerlo está "
                          "bien — crearlo es parte del programa.",
                },
                "options": [
                    {"value": "yes", "label": {"en": "Yes", "es": "Sí"}},
                    {"value": "no", "label": {"en": "No", "es": "No"}},
                    {"value": "unsure", "label": {"en": "Not sure", "es": "No estoy seguro"}},
                ],
            },
            {
                "name": "platforms", "type": "checkbox", "span": True,
                "label": {"en": "Where are you active today?",
                          "es": "¿Dónde estás activo hoy?"},
                "options": [
                    {"value": "facebook", "label": {"en": "Facebook", "es": "Facebook"}},
                    {"value": "instagram", "label": {"en": "Instagram", "es": "Instagram"}},
                    {"value": "tiktok", "label": {"en": "TikTok", "es": "TikTok"}},
                    {"value": "whatsapp", "label": {"en": "WhatsApp Business", "es": "WhatsApp Business"}},
                    {"value": "yelp", "label": {"en": "Yelp", "es": "Yelp"}},
                    {"value": "nextdoor", "label": {"en": "Nextdoor", "es": "Nextdoor"}},
                    {"value": "none", "label": {"en": "None of these", "es": "Ninguno"}},
                ],
            },
            {
                "name": "biggest_problem", "type": "textarea", "span": True, "rows": 3,
                "label": {"en": "What's the biggest problem with how you show up online?",
                          "es": "¿Cuál es el mayor problema con tu presencia en línea?"},
                "placeholder": {
                    "en": "\"Nobody finds us on Google\" · \"The site looks bad on a phone\" "
                          "· \"We get calls, but not the right jobs\"",
                    "es": "«Nadie nos encuentra en Google» · «El sitio se ve mal en el "
                          "teléfono» · «Recibimos llamadas, pero no los trabajos correctos»",
                },
            },
        ],
    },
    {
        "id": "goals",
        "legend": {"en": "What you want to grow", "es": "Lo que quieres hacer crecer"},
        "note": {
            "en": "This is what shapes the site — and what we build the local SEO around.",
            "es": "Esto define el sitio — y es la base del SEO local que construimos.",
        },
        "two_up": True,
        "fields": [
            {
                "name": "primary_service", "type": "text",
                "label": {"en": "Which service do you most want more of?",
                          "es": "¿De qué servicio quieres más trabajo?"},
                "placeholder": {"en": "Roof replacements", "es": "Cambios de techo"},
            },
            {
                "name": "typical_job_value", "type": "text",
                "label": {"en": "What's a typical job worth?",
                          "es": "¿Cuánto vale un trabajo típico?"},
                "placeholder": {"en": "$400 · $5,000 · varies a lot",
                                "es": "$400 · $5,000 · varía mucho"},
                "hint": {
                    "en": "A rough range is fine. It tells us what one extra lead a "
                          "month is actually worth to you.",
                    "es": "Un rango aproximado está bien. Nos dice cuánto vale realmente "
                          "un cliente más al mes.",
                },
            },
            {
                "name": "target_customer", "type": "text", "span": True,
                "label": {"en": "Who's the ideal customer for that work?",
                          "es": "¿Quién es el cliente ideal para ese trabajo?"},
                "placeholder": {"en": "Homeowners in Albany and Corvallis, 35+",
                                "es": "Dueños de casa en Albany y Corvallis, 35+"},
            },
            {
                "name": "primary_goal", "type": "radio", "span": True,
                "label": {"en": "What's the main thing the new site has to do?",
                          "es": "¿Cuál es la meta principal del nuevo sitio?"},
                "options": [
                    {"value": "calls", "label": {"en": "Get the phone ringing",
                                                 "es": "Que suene el teléfono"}},
                    {"value": "bookings", "label": {"en": "Fill the schedule",
                                                    "es": "Llenar la agenda"}},
                    {"value": "quotes", "label": {"en": "More quote requests",
                                                  "es": "Más solicitudes de cotización"}},
                    {"value": "foot_traffic", "label": {"en": "More people through the door",
                                                        "es": "Más visitas al local"}},
                    {"value": "credibility", "label": {"en": "Look as good as we actually are",
                                                       "es": "Vernos tan bien como realmente somos"}},
                ],
            },
        ],
    },
    {
        "id": "finish",
        "legend": {"en": "Last thing", "es": "Lo último"},
        "note": {
            "en": "Then you're done.",
            "es": "Y listo.",
        },
        "two_up": False,
        "fields": [
            {
                "name": "preferred_language", "type": "radio",
                "label": {"en": "Which language would you rather we worked in?",
                          "es": "¿En qué idioma prefieres que trabajemos?"},
                "hint": {
                    "en": "Calls, emails and the site itself — all of it can be either.",
                    "es": "Llamadas, correos y el sitio mismo — todo puede ser en cualquiera.",
                },
                "options": [
                    {"value": "en", "label": {"en": "English", "es": "Inglés"}},
                    {"value": "es", "label": {"en": "Español", "es": "Español"}},
                ],
            },
            {
                "name": "notes", "type": "textarea", "rows": 4,
                "label": {"en": "Anything else we should know?",
                          "es": "¿Algo más que debamos saber?"},
                "placeholder": {
                    "en": "A deadline, a competitor you're losing to, something you've "
                          "already tried…",
                    "es": "Una fecha límite, un competidor que te está ganando, algo que "
                          "ya intentaste…",
                },
            },
        ],
    },
]
