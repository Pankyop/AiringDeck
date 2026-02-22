# Technical Analysis: Multithreading & Multi-core in AiringDeck

This analysis reviews multithreading adoption and multi-core usage to improve
performance and user experience.

## 1. Current state (v3.x)

The application already uses multithreading strategically:

- **Async I/O operations**: AniList API calls (list sync, user profile) run via
  `QThreadPool`, preventing UI freezes while waiting for network responses.
- **UI rendering**: the QML engine (QtQuick) handles image loading and animations
  on threads separate from main app logic.

## 2. Does using more cores/threads make sense?

### Non-technical answer (UX)

Yes, but only for specific tasks.
The app is already fluid because heavy tasks (data download) happen in the
background. Adding more threads does not automatically make it faster if network
speed is the bottleneck, but it helps keep UI responsiveness under load.

### Technical answer (Python/Qt architecture)

Python has the **GIL (Global Interpreter Lock)**, which prevents true parallel
execution of pure Python CPU-bound code across cores. However:

1. **I/O-bound tasks (network/disk)**: multithreading is a good fit.
2. **CPU-bound tasks (data processing)**: for very large datasets and complex
   processing, `multiprocessing` can leverage multiple cores. For current loads
   (dozens/hundreds of anime), Qt threading is the best tradeoff for memory and complexity.

## 3. Potential future improvements

| Area | Benefit | Suggested technique |
| :--- | :--- | :--- |
| **Image pre-caching** | Download covers in background before user opens details. | `QRunnable` + `QThreadPool` |
| **Background sync** | Periodic automatic sync without manual action. | Low-priority dedicated `QThread` |
| **Heavy export/reporting** | Generate complex reports/statistics. | `multiprocessing` (to bypass GIL) |

## Conclusion

The current architecture is optimized for multithreading in terms of UI
responsiveness. True multi-core parallel compute is not currently required by
the data profile, but the app can evolve toward it if needed.
