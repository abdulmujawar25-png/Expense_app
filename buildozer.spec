[app]
title = ExpenseApp
package.name = expenseapp
package.domain = org.test
source.dir = .
source.include_exts = py
version = 0.1
requirements = python3,kivy,kivymd,sqlite3
orientation = portrait
fullscreen = 0

# Android specific
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.build_tools = 33.0.2

[buildozer]
log_level = 2
warn_on_root = 1
