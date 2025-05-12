# BlockHarness for Android

This document outlines the steps taken to adapt BlockHarness for Android deployment.

## Implemented Changes

1. **Touch Input Handling**
   - Removed keyboard controls and replaced with touch interactions
   - Added touch position scaling to handle different screen resolutions
   - Implemented touch-friendly UI elements with appropriate sizing
   - Fixed floating-point to integer conversion for grid coordinates

2. **Settings Button**
   - Added a settings button in the top-right corner
   - Improved touch target size for better usability on mobile devices

3. **Responsive Resolution**
   - Implemented dynamic scaling to fit device screen width
   - Maintained aspect ratio while filling the available screen space
   - Added helper functions for scaling UI elements consistently

## Testing Touch Handling

To test touch coordinate handling and scaling, you can run the included test script:

```bash
python android_test.py
```

This script verifies that:
- Touch coordinates are properly scaled according to screen size
- Grid positions are correctly calculated from touch coordinates
- All coordinates are properly converted to integers where needed

## Building for Android

To build the game for Android, you'll need to use Buildozer. Follow these steps:

1. Install Buildozer:
   ```bash
   pip install buildozer
   ```

2. Create a buildozer.spec file in the root of your project with the following content:
   ```ini
   [app]
   
   # Title of your application
   title = BlockHarness
   
   # Package name
   package.name = blockharness
   
   # Package domain (needed for android/ios packaging)
   package.domain = org.blockharness
   
   # Source code where the main.py lives
   source.dir = .
   
   # Source files to include
   source.include_exts = py,png,jpg,ico,ttf,json
   
   # Application version
   version = 1.0
   
   # Application requirements
   requirements = python3,kivy,pygame
   
   # Icon of the application
   icon.filename = ico.ico
   
   # Supported orientation (portrait, landscape or all)
   orientation = portrait
   
   # Android specific
   android.permissions = INTERNET
   
   # Android API to use
   android.api = 33
   
   # Android minAPI
   android.minapi = 21
   
   # Android SDK version to use
   android.sdk = 33
   
   # Android NDK version to use
   android.ndk = 23b
   
   # Android arch to build for (armeabi-v7a, arm64-v8a, x86, x86_64)
   android.arch = arm64-v8a
   
   # Android presplash background color (for android 5.0+)
   android.presplash_color = #000000
   
   # Android logcat filters
   android.logcat_filters = *:S python:D
   
   # Whether the application should be fullscreen or not
   fullscreen = 1
   
   # Kivy version
   android.allow_backup = True
   
   # Python-for-android bootstrap to use
   p4a.bootstrap = sdl2
   
   # Source include patterns
   source.include_patterns = play.py,*.png,*.jpg,*.ico,*.ttf,*.json,engine/*,ui/*,config/*
   
   # Main entry point - use play.py's main function
   android.entrypoint = play:main
   ```

3. Initialize the buildozer project:
   ```bash
   buildozer init
   ```

4. Build the APK:
   ```bash
   buildozer android debug
   ```

5. Install on your device:
   ```bash
   buildozer android deploy run
   ```

## Testing

To test the Android-adapted UI on desktop before deploying:

1. Run the game as usual:
   ```bash
   python play.py
   ```

2. The game will now use touch-friendly controls and responsive scaling.

## Notes for Further Enhancement

- Consider adding vibration feedback for touch interactions
- Implement Android-specific back button handling
- Add on-screen controls if needed for specific game actions
- Test on various device sizes to ensure responsive design works well 