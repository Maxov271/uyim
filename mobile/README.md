# Uyim.uz — Mobile (Phase 2 skeleton)

This is a **starting point**, not a runnable app yet. See
[`../docs/MOBILE_APP_PLAN.md`](../docs/MOBILE_APP_PLAN.md) for the full plan (screens, tech
stack, native features, rollout).

What's here is the framework-agnostic TypeScript that doesn't depend on Expo's project
generator, so it could be written and reasoned about directly:

- `src/theme/tokens.ts` — design tokens ported 1:1 from `frontend/assets/css/app.css`
- `src/api/client.ts` + `src/api/types.ts` — full API client for the Django backend (`../backend`),
  the same contract `frontend/assets/js/api.js` uses
- `src/store/useAppStore.ts` — local favorites/compare/theme state shape

## To continue this

```bash
npx create-expo-app@latest . --template blank-typescript
# then copy src/theme, src/api, src/store into the generated project as-is
npm install expo-router expo-secure-store @tanstack/react-query zustand \
  @react-native-async-storage/async-storage
```

Then build screens per the plan's screen map, wiring them to `api` from `src/api/client.ts`.
Set `EXPO_PUBLIC_API_BASE` to point at a running backend (`http://<your-ip>:8000/api` for a
physical device on the same network, since `localhost` won't resolve to your dev machine from
the phone).
