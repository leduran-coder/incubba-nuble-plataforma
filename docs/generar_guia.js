const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LevelFormat, AlignmentType, ExternalHyperlink,
} = require("docx");

const MORADO = "7A4FBF";
const NAVY = "2A3F56";
const GRIS = "52514E";

const numbering = {
  config: [
    {
      reference: "bullets",
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ],
    },
    ...["paso1", "paso2", "paso3", "paso4", "paso5"].map((reference) => ({
      reference,
      levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ],
    })),
  ],
};

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function pBold(text) {
  return new Paragraph({ children: [new TextRun({ text, bold: true })], spacing: { after: 100 } });
}
function bullet(text, level = 0) {
  return new Paragraph({
    children: [new TextRun({ text })],
    numbering: { reference: "bullets", level },
    spacing: { after: 80 },
  });
}
function numbered(text, ref = "paso1") {
  return new Paragraph({
    children: [new TextRun({ text })],
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80 },
  });
}
function code(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Consolas", size: 20, color: NAVY })],
    shading: { type: ShadingType.CLEAR, fill: "F4F1FA" },
    spacing: { after: 120 },
    border: {
      top: { style: BorderStyle.SINGLE, size: 2, color: "ECE7F5" },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: "ECE7F5" },
      left: { style: BorderStyle.SINGLE, size: 2, color: "ECE7F5" },
      right: { style: BorderStyle.SINGLE, size: 2, color: "ECE7F5" },
    },
  });
}
function nota(text) {
  return new Paragraph({
    children: [new TextRun({ text: "Nota: " + text, italics: true, color: GRIS })],
    spacing: { after: 160 },
  });
}
function link(textVisible, url) {
  return new Paragraph({
    children: [new ExternalHyperlink({
      link: url,
      children: [new TextRun({ text: textVisible, style: "Hyperlink" })],
    })],
    spacing: { after: 120 },
  });
}

function simpleTable(headers, rows, widths) {
  const totalWidth = 9000;
  const w = widths || headers.map(() => Math.floor(totalWidth / headers.length));
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((htext, i) => new TableCell({
      width: { size: w[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: NAVY },
      children: [new Paragraph({ children: [new TextRun({ text: htext, bold: true, color: "FFFFFF" })] })],
    })),
  });
  const bodyRows = rows.map((row) => new TableRow({
    children: row.map((cell, i) => new TableCell({
      width: { size: w[i], type: WidthType.DXA },
      children: [new Paragraph({ children: [new TextRun({ text: cell })] })],
    })),
  }));
  return new Table({ columnWidths: w, width: { size: totalWidth, type: WidthType.DXA }, rows: [headerRow, ...bodyRows] });
}

const doc = new Document({
  numbering,
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 22 } },
    },
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      new Paragraph({
        children: [new TextRun({ text: "Guía de despliegue", bold: true, size: 56, color: MORADO })],
        spacing: { after: 80 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Plataforma de Postulación y Evaluación — Incubba Ñuble UBB, Generación 2026", size: 28, color: NAVY })],
        spacing: { after: 60 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Guía paso a paso pensada para alguien SIN conocimientos de programación.", italics: true, color: GRIS })],
        spacing: { after: 400 },
      }),

      h1("1. Qué construimos"),
      p("Se desarrolló una plataforma web propia (no depende de Google Forms) para Incubba Ñuble UBB, con:"),
      bullet("Importación de las postulaciones ya recibidas por el formulario actual (a través de un archivo CSV)."),
      bullet("Evaluación en línea siguiendo exactamente las 3 rúbricas de las bases: Admisibilidad, Evaluación de proyecto y Entrevista personal."),
      bullet("Una bonificación adicional configurable por \"potencial dinámico\", basada en la definición de CORFO citada en las bases (crecimiento superior al 20% anual)."),
      bullet("Un ranking final con el puntaje combinado, resaltando el cupo máximo de 40 y las metas de paridad de género y cobertura comunal."),
      bullet("Un panel de estadísticas: género, provincia/comuna, estado de formalización, tipo de innovación, financiamiento previo, sectores, etc."),
      bullet("Acceso con usuario y contraseña propios, con roles de administrador/a y evaluador/a."),
      p("La app está construida en Python con Streamlit (la interfaz) y una base de datos propia (no depende de que la planilla de Google seguirá existiendo). Todo el código fuente se entrega junto con esta guía."),

      h1("2. Qué necesitas antes de empezar"),
      p("Todo lo que se usa aquí tiene un plan gratuito suficiente para este proyecto (hasta 40 cupos y unas pocas decenas de evaluadores). Vas a necesitar crear 3 cuentas gratuitas, en este orden:"),
      simpleTable(
        ["Servicio", "Para qué se usa", "Enlace"],
        [
          ["GitHub", "Guardar el código de la plataforma (como una carpeta en la nube)", "github.com"],
          ["Supabase", "Base de datos donde se guardan postulaciones y evaluaciones", "supabase.com"],
          ["Streamlit Community Cloud", "Publicar la app como una página web", "share.streamlit.io"],
        ],
        [2600, 4400, 2000],
      ),
      nota("No necesitas escribir ni una línea de código. Solo vas a hacer clics y copiar/pegar un par de datos entre estos 3 sitios."),

      h1("3. Paso 1 · Subir el proyecto a GitHub"),
      numbered("Entra a github.com y crea una cuenta gratuita (si no tienes una)."),
      numbered("Arriba a la derecha, haz clic en el símbolo “+” y elige “New repository”."),
      numbered("Ponle un nombre, por ejemplo: incubba-nuble-plataforma. Déjalo como “Public” o “Private” (ambos funcionan). No marques ninguna otra opción. Haz clic en “Create repository”."),
      numbered("En la página del repositorio recién creado, busca el enlace “uploading an existing file” (o el botón “Add file → Upload files”)."),
      numbered("Arrastra TODOS los archivos y carpetas del proyecto que te entregamos (la carpeta completa \"incubba-platform\") a esa pantalla."),
      numbered("Escribe un mensaje como “Primera versión” y haz clic en “Commit changes”."),
      nota("Si nunca has usado GitHub, también puedes pedirle a cualquier persona con conocimientos básicos de computación que haga este paso por ti en 5 minutos; no requiere saber programar, solo subir archivos."),

      h1("4. Paso 2 · Crear la base de datos gratuita en Supabase"),
      numbered("Entra a supabase.com y crea una cuenta gratuita (puedes usar tu cuenta de GitHub para entrar más rápido).", "paso2"),
      numbered("Haz clic en “New project”. Elige un nombre (por ejemplo “incubba-nuble”) y crea una contraseña segura para la base de datos — GUÁRDALA, la necesitarás en el paso siguiente.", "paso2"),
      numbered("Espera 1-2 minutos mientras Supabase crea el proyecto.", "paso2"),
      numbered("Ve a “Project Settings” (ícono de engranaje) → “Database”.", "paso2"),
      numbered("Busca la sección “Connection string” y elige el modo “URI”. Copia ese texto — empieza con postgresql://...", "paso2"),
      numbered("Reemplaza la parte [YOUR-PASSWORD] de ese texto por la contraseña que creaste en el paso 2. Guarda este texto completo, lo vas a pegar en el paso 5.", "paso2"),
      nota("El plan gratuito de Supabase pausa el proyecto si nadie lo usa por 7 días seguidos. Si eso pasa, basta con entrar al panel de Supabase y hacer clic en “Restore project” — los datos NO se pierden."),

      h1("5. Paso 3 · Publicar la app en Streamlit Community Cloud"),
      numbered("Entra a share.streamlit.io e ingresa con tu cuenta de GitHub.", "paso3"),
      numbered("Haz clic en “New app”.", "paso3"),
      numbered("Elige el repositorio que subiste en el Paso 1 (incubba-nuble-plataforma), la rama “main” y como “Main file path” escribe: app.py", "paso3"),
      numbered("Antes de hacer clic en “Deploy”, abre la sección “Advanced settings…”.", "paso3"),
      numbered("En el cuadro “Secrets”, pega exactamente esto (reemplazando el valor por el connection string del Paso 2):", "paso3"),
      code('DATABASE_URL = "postgresql://postgres:TU_PASSWORD@TU_PROYECTO.supabase.co:5432/postgres"'),
      numbered("Haz clic en “Deploy”. En 2-3 minutos la plataforma va a estar publicada, con una dirección web propia (algo como https://incubba-nuble.streamlit.app).", "paso3"),
      nota("Esa dirección web es la que compartes con el resto del equipo evaluador. Cada vez que alguien entra, se conecta a la misma base de datos en Supabase, así que todos ven la misma información en tiempo real."),

      h1("6. Paso 4 · Primer ingreso"),
      p("La primera vez que alguien entra a la plataforma, ya existe un usuario administrador de fábrica:"),
      simpleTable(["Correo", "Contraseña"], [["admin@incubba.cl", "incubba2026"]], [4500, 4500]),
      numbered("Ingresa con esos datos.", "paso4"),
      numbered("Ve a Configuración → “Mi cuenta” y cambia la contraseña de inmediato por una solo tuya.", "paso4"),
      numbered("Ve a Configuración → “Evaluadores” y crea una cuenta para cada integrante del panel de evaluación, con su propio correo y una contraseña temporal (cada evaluador/a puede cambiarla luego desde “Mi cuenta”).", "paso4"),

      h1("7. Paso 5 · Importar las postulaciones"),
      numbered("Abre la hoja de cálculo de Google (“Respuestas”) vinculada al formulario de postulación.", "paso5"),
      numbered("Ve a Archivo → Descargar → Valores separados por comas (.csv).", "paso5"),
      numbered("En la plataforma, ve a Configuración → “Importar postulaciones” y sube ese archivo.", "paso5"),
      numbered("Revisa el mapeo de columnas que la plataforma sugiere automáticamente (qué columna del CSV corresponde a qué campo). Ajusta manualmente cualquiera que no calce.", "paso5"),
      numbered("Haz clic en “Importar postulaciones”. Puedes repetir este proceso cada vez que lleguen postulaciones nuevas: la plataforma detecta y omite automáticamente las que ya habías importado (por RUN o correo).", "paso5"),

      h1("8. Uso diario de la plataforma"),
      h2("Evaluación"),
      p("Cada evaluador/a entra con su cuenta, va a “Evaluación”, elige una postulación y califica las 3 etapas (Admisibilidad, Proyecto, Entrevista) según la rúbrica exacta de las bases, más la pestaña de Bonificación por potencial dinámico. El puntaje final se calcula automáticamente como el promedio entre todos los evaluadores que calificaron cada postulación."),
      h2("Resultados"),
      p("La página “Resultados” muestra el ranking final ordenado, resaltando el cupo máximo de 40 y avisando si no se cumple la meta de al menos 50% de proyectos liderados por mujeres, para que el panel pueda hacer el ajuste manual que indican las bases (punto 4.4, aplicado DESPUÉS del ranking por rúbrica)."),
      h2("Estadísticas"),
      p("La página “Estadísticas” entrega una vista general en cualquier momento: género, provincia/comuna, tipo de emprendimiento, tipo de innovación, sectores más frecuentes, financiamiento previo, etc."),

      h1("9. Cómo ajustar la bonificación por potencial dinámico"),
      p("Las bases NO definen literalmente esta bonificación — se construyó especialmente para este proyecto a partir de la definición de emprendimiento dinámico de CORFO (crecer sobre 20% anual, duplicar el negocio cada 3-4 años). Se calcula así por defecto, y todo es ajustable sin tocar código, desde Configuración → “Bonificación”:"),
      simpleTable(
        ["Factor", "Fuente", "Peso por defecto"],
        [
          ["Tipo de potencial innovador (marginal/incremental/disruptiva)", "Declarado por el postulante en el formulario", "30%"],
          ["Alcance proyectado (regional/nacional/internacional)", "Declarado por el postulante", "25%"],
          ["Financiamiento público o privado ya levantado", "Declarado por el postulante", "15%"],
          ["Ambición y credibilidad de la proyección a 3 años", "Calificado por el panel evaluador (escala 1 a 5)", "30%"],
        ],
        [4200, 3200, 1600],
      ),
      p("El resultado se suma como puntos extra (hasta un máximo configurable, 10 puntos por defecto) sobre el puntaje final de 100. Desde la misma página también se ajusta cuánto pesa cada etapa (proyecto vs. entrevista) en el puntaje final."),

      h1("10. Mantenimiento, respaldos y límites de los planes gratuitos"),
      bullet("Respaldo manual: en “Resultados” hay un botón “Descargar ranking como CSV”. Se recomienda descargarlo cada vez que se cierre una etapa de evaluación importante."),
      bullet("Supabase (gratis): hasta 500 MB de base de datos — más que suficiente para varios años de convocatorias. Pausa proyectos inactivos 7+ días; se reactivan con un clic."),
      bullet("Streamlit Community Cloud (gratis): la app “duerme” tras un período largo sin visitas y despierta sola (con ~30 segundos de espera) en la primera visita del día."),
      bullet("Usuarios y contraseñas: solo un administrador/a puede crear evaluadores/as y resetear configuración; cualquier evaluador/a puede cambiar su propia contraseña desde “Mi cuenta”."),

      h1("11. Qué NO incluye esta primera versión (posible fase 2)"),
      p("Para que la primera versión estuviera lista rápido y fuera simple de publicar, quedaron fuera de este alcance — y se pueden agregar más adelante si se necesitan:"),
      bullet("Formulario propio de postulación (por ahora se sigue usando el Google Form actual y se importa el CSV; se podría reemplazar por un formulario nativo de la plataforma)."),
      bullet("Sincronización automática y en vivo con la Google Sheet (hoy se hace por subida de CSV, cada vez que se quiera actualizar)."),
      bullet("Notificaciones automáticas por correo a postulantes seleccionados."),
      bullet("Reproducción embebida del video-pitch dentro de la plataforma (hoy se abre el enlace aparte)."),

      h1("12. Soporte"),
      p("Todo el código fuente, junto con esta guía y un set de datos de ejemplo para practicar sin usar información real, se entrega junto a este documento. Cualquier ajuste al motor de rúbrica vive en un solo archivo (config/rubric.py), pensado para que sea fácil de mantener incluso por alguien nuevo en el equipo técnico."),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("/root/incubba-platform/docs/Guia_de_despliegue_Incubba_Nuble.docx", buffer);
  console.log("Documento generado.");
});
