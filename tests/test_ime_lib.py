"""Static structure checks for the ime-lib split (Gradle itself is UNMEASURED without an Android SDK).

The TT9 app must keep its applicationId and launcher, and consume the IME as the `ime-lib` library
module, whose source sets point at the existing app/src tree (no copied files)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: (ROOT / p).read_text(encoding="utf-8")


def test_settings_includes_both_modules():
	s = read("settings.gradle")
	assert "include ':app'" in s
	assert "include ':ime-lib'" in s


def test_app_keeps_application_id_and_depends_on_lib():
	b = read("app/build.gradle")
	assert "id 'com.android.application'" in b
	assert re.search(r"applicationId\s*=\s*PACKAGE_NAME", b)
	assert "implementation project(':ime-lib')" in b
	assert "ext.PACKAGE_NAME = \"io.github.sspanak.${APP_NAME}\"" in read("app/constants.gradle")
	assert "ext.APP_NAME = 'tt9'" in read("app/constants.gradle")


def test_app_does_not_compile_the_sources_twice():
	b = read("app/build.gradle")
	assert re.search(r"java\.srcDirs\s*=\s*\[\]", b), "app must not compile the library's java tree"
	assert "src/app/AndroidManifest.xml" in b


def test_lib_is_a_library_over_the_app_tree():
	b = read("ime-lib/build.gradle")
	assert "id 'com.android.library'" in b
	assert "namespace = PACKAGE_NAME" in b
	for d in ("java", "res", "assets"):
		assert "../app/src/${n}/" + d in b, "source set must point at the existing app/src tree: " + d
	for f in ("VERSION_CODE", "VERSION_FULL", "DICTIONARY_EXTENSION", "DOCS_DIR", "DONATION_URL", "LITE"):
		assert f in b, "library must define BuildConfig." + f
	assert "tt9.bundledDictionaries" in b


def test_manifests_split_launcher_from_ime():
	lib = read("app/src/main/AndroidManifest.xml")
	app = read("app/src/app/AndroidManifest.xml")
	assert "android.permission.BIND_INPUT_METHOD" in lib and "@xml/method" in lib
	assert "android.intent.category.LAUNCHER" not in lib
	assert "android.intent.category.LAUNCHER" in app
	assert "versionCode" in app


def test_constants_are_not_rootdir_bound():
	assert "project.rootDir" not in read("app/constants.gradle")
