# math-speak 🔊➗

Hear LaTeX math as words, not symbols. A Hermes Agent plugin that rewrites
`$v = c_1 v_1$` into *"v equals c sub 1 v sub 1"* before speech synthesis —
so read-aloud no longer says *"dollar vee underscore one dollar"*.

Handles inline (`$...$`, `\(...\)`), display (`$$...$$`, `\[...\]`) math,
fractions, roots, sums/integrals with limits, sub/superscripts, Greek letters
and operators. Currency (`$5`, `US$300`) is deliberately left alone.

## What you get

| Piece | Name | Notes |
|---|---|---|
| Agent tool | `math_speak_text` (toolset `tts`) | Zero dependencies. The agent calls it to make any text speakable. |
| TTS provider | `mathspeak` | Math-aware synthesis through free Microsoft Edge TTS. Needs `edge-tts`. |

## Install (ask your Hermes agent)

Just say:

> Install the plugin from https://github.com/helloworldtryin/hermes-math-speak

The agent will run:

```bash
hermes plugins install https://github.com/helloworldtryin/hermes-math-speak
hermes plugins enable math-speak
```

Then restart the backend (`/restart`, or relaunch the desktop app).

## Install (manual)

```bash
git clone https://github.com/helloworldtryin/hermes-math-speak
cp -r hermes-math-speak ~/.hermes/plugins/math-speak   # Windows: %LOCALAPPDATA%\hermes\plugins\math-speak
hermes plugins enable math-speak
```

For the `mathspeak` voice provider also install:

```bash
pip install edge-tts    # or: uv pip install edge-tts
```

## Use

**A. Automatic (recommended).** Route all speech through it:

```bash
hermes config set tts.provider mathspeak
```

Every read-aloud, voice reply and TTS call now converts math first.
Optional voice override: `MATHSPEAK_VOICE` env var (default `en-US-AriaNeural`).

**B. Per-message.** Ask the agent for a speakable version, or let it call the
`math_speak_text` tool itself before speaking.

**C. Standalone.** The converter is dependency-free:

```bash
python -c "import sys; sys.path.insert(0, '.'); from mathtext import speak_math; print(speak_math('Half: $\\frac{1}{2}$'))"
# Half: 1 over 2
```

## Verify your setup

```bash
hermes plugins list                 # math-speak present and enabled
hermes plugins validate ~/.hermes/plugins/math-speak
cd ~/.hermes/plugins/math-speak && pytest tests/ -q   # 7 passed
```

Quick listening test — have the agent read this aloud:

> A basis of $\mathbb{R}^2$ is $e_1 = (1,0)$, $e_2 = (0,1)$, and $\sum_{i=1}^{n} x_i$ converges.

You should hear: *"A basis of R 2 is e sub 1 equals 1 0, e sub 2 equals 0 1, and sum from i equals 1 to n, x sub i converges."*

## Uninstall

```bash
hermes plugins disable math-speak
hermes plugins remove math-speak
```

## Compatibility

Built against the Hermes [general plugin + TTS provider surfaces](https://github.com/NousResearch/hermes-agent)
(`register_tool`, `register_tts_provider`, `TTSProvider.synthesize`). If a
future Hermes release changes those APIs, `hermes plugins doctor` will flag it —
please open an issue.

## License

MIT — see [LICENSE](LICENSE).
