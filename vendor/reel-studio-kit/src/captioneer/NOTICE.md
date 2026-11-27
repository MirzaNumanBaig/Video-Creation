# Third-party notice

The files in this folder are copied from **remotion-captioneer** by Shuvo Roy
(https://github.com/neutral-Stage/remotion-captioneer, commit e86e738, MIT licence, see `LICENSE`).

Changes made here: only the caption style components, presets, animation helpers and types were copied
(no speech-to-text providers, CLI, hosting or preview server); `types.ts` defines the `Caption` and
`TikTokPage` types locally instead of importing `@remotion/captions`. Nothing in this folder calls the network.
