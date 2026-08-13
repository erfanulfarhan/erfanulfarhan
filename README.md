<div align="center">

<img src="./ascii.svg" width="460" alt="Erfanul Hakim Farhan"/>

<img src="./stats.svg" width="620" alt="Contributions in the last year"/>

[portfolio](https://github.com/erfanulfarhan/portfolio) &nbsp;·&nbsp;
[sitesage](https://sitesage-erfanul.vercel.app) &nbsp;·&nbsp;
[ask my docs](https://ask-my-docs-erfanul.vercel.app) &nbsp;·&nbsp;
[email](mailto:ershadul@datacenters.com)

</div>

<img src="./hd-about.svg" width="620" alt="about"/>

> AI and automation developer.<br>
> Small tools that do one job, shipped and actually used.

Most of what I build starts as a problem I hit myself: a ticket that sells out<br>
before I can click, a results PDF nobody wants to read, notes I need answers<br>
from at 2am. I put the AI where it earns its place and write plain code for<br>
everything else.

<img src="./hd-stack.svg" width="620" alt="stack"/>

<samp>python &nbsp; javascript &nbsp; typescript &nbsp; react &nbsp; node &nbsp; playwright &nbsp; fastapi &nbsp; supabase &nbsp; postgres &nbsp; vercel &nbsp; git</samp>

<img src="./hd-projects.svg" width="620" alt="projects"/>

**[exam-toolkit](https://github.com/erfanulfarhan/exam-toolkit)** &nbsp;·&nbsp; <samp>typescript, react</samp><br>
Revision tools for Edexcel International A Level and IGCSE. UMS grade calculator<br>
built off the published boundaries, past papers beside mark schemes that stay<br>
locked until you attempt the question, mock timer and study planner.

**[sitesage](https://github.com/erfanulfarhan/sitesage)** &nbsp;·&nbsp; <samp>javascript, groq</samp><br>
Embeddable AI chat widget for any site. Create a bot, train it on text or URLs,<br>
drop in one script tag. Multi-tenant, so one deployment serves every customer.

**[ask-my-docs](https://github.com/erfanulfarhan/ask-my-docs)** &nbsp;·&nbsp; <samp>javascript, pgvector</samp><br>
RAG over your own PDFs and notes, with citations back to the source. Embeddings<br>
run in the browser; Supabase pgvector does the search.

**[cineplex-bot](https://github.com/erfanulfarhan/cineplex-bot)** &nbsp;·&nbsp; <samp>python, playwright</samp><br>
Telegram bot for Star Cineplex: live seat availability, seat-map images, and<br>
standing orders that book the moment tickets go on sale.

**[friday-voice](https://github.com/erfanulfarhan/friday-voice)** &nbsp;·&nbsp; <samp>typescript, react</samp><br>
Aria, a browser voice assistant on the Web Speech API with Llama 3.3 70B<br>
behind it. No install, no native app.

**[bracu-result-watch](https://github.com/erfanulfarhan/bracu-result-watch)** &nbsp;·&nbsp; <samp>python</samp><br>
Watches a university notice board and alerts by iMessage, email or Telegram the<br>
moment a result document appears.

<img src="./hd-stats.svg" width="620" alt="stats"/>

<div align="center">

<img src="./langs.svg" width="620" alt="Top languages by bytes and by repo"/>

<img src="./year.svg" width="620" alt="The last year, one character per day"/>

</div>

<img src="./hd-about-this-page.svg" width="620" alt="about this page"/>

Every graphic here is generated in this repository, not embedded from someone<br>
else's server, so nothing on the page can rate-limit or go dark. `ascii.svg` is<br>
a photo pushed through a character ramp by<br>
[`scripts/make_portrait.py`](scripts/make_portrait.py). The stat graphics and<br>
the section headings are drawn by [a scheduled action](.github/workflows/stats.yml)<br>
from the GitHub GraphQL API once a day, committing only what changed.

They animate with SMIL inside the SVG, because GitHub strips scripts from<br>
READMEs. The headings are images for the same reason: GitHub strips CSS too, so<br>
an image is the only way to put this page's own typeface on a heading.

The typeface is [JetBrains Mono](scripts/fonts), subset to just the characters<br>
each graphic uses and inlined as base64. That is not only for looks: the<br>
portrait's grid assumes an advance width of exactly 0.600 em, and a viewer whose<br>
default monospace is narrower would see it squeezed.

Language totals cover public repositories only. `year.svg` draws one character<br>
per day on a four step ramp: `:` `+` `#` `@`, quiet to loud.

<sub>Built with the approach in <a href="https://agreeable-credit-859.notion.site/A-GitHub-profile-that-generates-itself-3abedfe9a65a81e4afc9daed90cb4e7e">A GitHub profile that generates itself</a>. Portrait pipeline and stat generator adapted from <a href="https://github.com/andriidrok1/andriidrok1">andriidrok1/andriidrok1</a>.</sub>
