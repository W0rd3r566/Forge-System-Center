# Платформы и готовые сборки Forge

[English version](PLATFORMS.en.md) · [Главная страница](../README.md) · [Последние релизы](https://github.com/W0rd3r566/Forge-System-Center/releases/latest)

Forge собирается **на самой целевой ОС и архитектуре**. Один Windows EXE не является Linux-сборкой, а ARM64-бинарник не заменяет x64-бинарник. GitHub Actions собирает каждую комбинацию отдельно, запускает тесты и прикладывает контрольные суммы к релизам.

## Поддерживаемая матрица

| Платформа | Архитектура | Формат |
| --- | --- | --- |
| Windows 10/11 | x64 (Intel/AMD, 64 bit) | ZIP с переносимым EXE |
| Windows 11 on Arm | ARM64 | ZIP с переносимым EXE |
| Debian/Ubuntu и производные | x86_64 | DEB, RPM, TAR.GZ |
| Современные Linux-дистрибутивы | ARM64/aarch64 | DEB, RPM, TAR.GZ |
| macOS | Intel x64 | ZIP с приложением .app |
| macOS | Apple Silicon ARM64 | ZIP с приложением .app |

**32-битная Windows (x86) не входит в матрицу.** Forge использует Qt 6 через PySide6, а текущие поддерживаемые PySide6 Windows wheels доступны для x64 и ARM64, но не для Win32. Без замены GUI-стека или самостоятельной сборки Qt обещать рабочий 32-битный EXE было бы неправильно. Аналогично, готовые Qt6-бинарники Forge не предназначены для 32-битного Linux.

## Какие файлы искать в релизе

Открой [страницу последних релизов](https://github.com/W0rd3r566/Forge-System-Center/releases/latest).

- **Windows:** ForgeSystemCenter-версия-windows-x64.zip или ForgeSystemCenter-версия-windows-arm64.zip. Распакуй архив и запусти ForgeSystemCenter.exe.
- **Debian, Ubuntu, Linux Mint, Pop!_OS и производные:** пакет forge-system-center_версия_amd64.deb или forge-system-center_версия_arm64.deb.
- **Fedora и RPM-совместимые дистрибутивы:** пакет forge-system-center-версия-1.x86_64.rpm или forge-system-center-версия-1.aarch64.rpm.
- **Arch, CachyOS, Manjaro и другие GNU/Linux:** ForgeSystemCenter-версия-linux-x86_64.tar.gz или ForgeSystemCenter-версия-linux-arm64.tar.gz. Архив не устанавливает системные пакеты сам.
- **macOS:** ForgeSystemCenter-версия-macos-x64.zip или ForgeSystemCenter-версия-macos-arm64.zip.

Каждый публичный GitHub Release также содержит SHA256SUMS.txt. Сверяй контрольную сумму загруженного файла, чтобы убедиться в целостности архива.

## Linux: совместимость

Linux-архивы собраны на Ubuntu 22.04 для x86_64 и Ubuntu 24.04 для ARM64. Это влияет на минимальную версию glibc:

| Архитектура | Минимальная glibc | Базовая среда сборки |
| --- | --- | --- |
| x86_64 | 2.35 | Ubuntu 22.04 |
| ARM64/aarch64 | 2.39 | Ubuntu 24.04 |

Из-за этого старые дистрибутивы могут не запускать готовый бинарник, даже если название пакета подходит. Для x86_64 обычно подходят современные Debian/Ubuntu и актуальные rolling-release дистрибутивы. Для ARM64 нужна система с glibc 2.39 или новее. Alpine Linux с musl не является целью этих готовых пакетов.

### DEB

Установи локальный пакет через графический менеджер пакетов или команду:

~~~bash
sudo apt install ./forge-system-center_<версия>_amd64.deb
~~~

Для ARM64 замени amd64 на arm64. apt должен иметь доступ к репозиториям с зависимостями пакета.

### RPM

На Fedora или совместимой системе установи скачанный RPM через менеджер пакетов, например:

~~~bash
sudo dnf install ./forge-system-center-<версия>-1.x86_64.rpm
~~~

На ARM64 используй файл aarch64. В openSUSE используй её штатный менеджер пакетов.

### TAR.GZ

~~~bash
tar -xzf ForgeSystemCenter-<версия>-linux-x86_64.tar.gz
cd ForgeSystemCenter-<версия>-linux-x86_64
./ForgeSystemCenter
~~~

Для ARM64 выбери архив с linux-arm64. При отсутствии X11/XWayland или необходимых системных библиотек Qt GUI может не запуститься. На Arch/CachyOS могут понадобиться пакеты libxcb, xcb-util-cursor, libxkbcommon, libxkbcommon-x11, mesa, libglvnd и dbus.

## Windows

Готовый ZIP — переносимая сборка, установщик не нужен. Распакуй архив в обычную папку, затем запусти ForgeSystemCenter.exe. Настройки Forge сохраняются отдельно в профиле текущего пользователя.

Сборки не подписаны сертификатом издателя, поэтому SmartScreen может показывать предупреждение о неизвестном издателе. Сверяй источник скачивания и SHA256SUMS.txt.

## macOS

Распакуй ZIP и перемести ForgeSystemCenter.app в Applications. Пакет для Intel предназначен для Intel Mac, а arm64 — для Apple Silicon. Приложения пока не подписываются и не нотарифицируются сертификатом Apple, поэтому macOS может показать предупреждение Gatekeeper.

## Запуск сборок и публикация

Workflow **Native builds and releases** можно запустить вручную во вкладке **Actions**. Его артефакты доступны в run в течение 30 дней. При публикации Git-тега вида v0.2.0 workflow автоматически собирает все цели, затем создаёт GitHub Release с архивами и SHA256SUMS.txt.

Проверки и упаковка выполняются на нативных runner-ах Windows, Linux и macOS, включая ARM64. Это повышает уверенность в сборке, но не заменяет тестирование на каждой модели устройства и каждом дистрибутиве.
