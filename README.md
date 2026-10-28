# PİL Stüdyo — Android (Capacitor)

Web uygulaması (`www/`) Capacitor ile Android'e sarılır; dosyalar uygulamanın içinde gelir, internetsiz çalışır.

## Yeni web sürümünü almak
    npm ci
    node scripts/prepare-www.mjs /path/to/pil-site-vX.zip   # fontları gömer, yedek alma düzeltmesini uygular
    npx cap sync android
Her Play yüklemesinde `android/app/build.gradle` içindeki `versionCode`'u 1 artır.

## .aab üretmek
- `main` dalına her push, GitHub Actions ile imzasız `app-release-unsigned.aab` üretir ve `aab-build` dalına koyar.
- İmzalamak (anahtar GitHub'a hiç gitmez):

      jarsigner -keystore pil-upload.keystore -signedjar pil-studyo-1.0.0.aab app-release-unsigned.aab pil-upload

- Alternatif: `android/keystore.properties` ve `android/pil-upload.keystore` dosyalarını koyup `gradle -p android bundleRelease`.

Keystore ve şifresi asla repoya eklenmez.
