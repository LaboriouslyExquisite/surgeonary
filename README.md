# Surgeonary

A surgeon's-eye training platform for surgical residents and medical students: watch cases live from the attending surgeon's point of view, find recordings on a 3D human body, follow trending techniques, prepare cases in 3D, and ask questions answered from the medical literature.

This is a prototype built for Cornell's Product Studio. Cases, surgeons, figures and profiles are sample content. It is for training and demonstration, not for clinical decisions.

## What's in it

**Platform**
- **Live surgery feed**: cases streamed from the surgeon's point of view.
- **Video library selection**: a 3D human body built from BodyParts3D anatomy scans. Pick a region to see its recordings.
- **Trending techniques**: what surgeons are watching this week, with the papers behind each technique.
- **3D rendering**: a pre-operative plan for a craniotomy, with the structures at risk.
- **Ask Surgeonary**: answers surgical questions only from papers it finds on PubMed and PubMed Central, and quotes the source sentence under every answer. See [Ask Surgeonary](#ask-surgeonary) below.
- **Surgeon Wearable**: the head-mounted camera that films the surgeon's view.

**Workspace**
- **Notes**: templates for case notes, pre-op prep, post-case debriefs and journal clubs.
- **Preference cards**: example surgeon preference cards with pull lists.
- **Research articles**: a reading list of real PubMed papers, a live PubMed search and a reader.
- **Profile**: an example resident profile (Dr. Okafor).

The landing page that introduces Surgeonary is `index.html`. The platform opens from its "Open the platform" button, or directly at `index.html#dash`.

## Run it on your computer

The app is plain HTML, CSS and JavaScript. There is nothing to install or build.

1. Download this repository (green **Code** button → **Download ZIP**) and unzip it, or clone it with Git.
2. Start a local web server in the folder:
   ```bash
   python3 -m http.server 8765
   ```
3. Open http://localhost:8765/index.html in your browser.

On a Mac you can instead double-click `start-surgeonary.command`. It starts the server, opens the app, and starts Ollama if it is installed. The first time, macOS may ask you to confirm that you want to open it.

The app needs an internet connection: it loads three.js and its font from public CDNs, and Ask Surgeonary and Research articles read from PubMed.

## Ask Surgeonary

Ask Surgeonary runs two open medical language models on your own computer through [Ollama](https://ollama.com):

- **MedGemma 4B** (Google) writes every answer and checks it.
- **Meditron 7B** (EPFL, built on Meta's Llama 2) writes a second attempt when MedGemma's answer does not hold up.

For each question it searches PubMed and PubMed Central, picks the sentences most likely to hold the answer, and lets the model answer only from those sentences. Each sentence of the answer is checked against the passage it cites; a sentence that the passage does not state is left out. The passage is shown word for word under the answer, with a link to the paper. If the papers do not state the answer, it says so instead of guessing.

To turn it on:

1. Install Ollama from https://ollama.com.
2. Download the two models (about 7 GB together):
   ```bash
   ollama pull medgemma:4b
   ollama pull meditron:7b
   ```
3. Open the app from `http://localhost` as above. Ask Surgeonary shows **Live model** when it can reach the models.

Ollama only accepts requests from pages served by your own computer. On any other address, such as GitHub Pages, the rest of the app works, but Ask Surgeonary explains that live answers run on the demo computer and does not answer.

The models are not part of this repository. Check their licences before you use them: MedGemma is under Google's Health AI Developer Foundations terms, and Meditron under the Llama 2 Community License.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app: landing page and platform |
| `platform.html` | Opens the platform dashboard directly |
| `body-*.js` | The 3D anatomy layers (skeleton, organs, vascular, nervous, head) |
| `photo-*.jpg` | The surgery photographs used as video stills |
| `start-surgeonary.command` | Mac launcher |
| `CREDITS.md` | Sources and licences for the anatomy, photos, fonts and libraries |

## Credits

Anatomy from BodyParts3D, © The Database Center for Life Science, licensed under CC BY 4.0. Photographs from Unsplash. Full details are in [CREDITS.md](CREDITS.md).
