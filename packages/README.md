# Package folders

One folder per package, named by its package id. A finished folder contains:

```text
package.yaml       required: the manifest Grimoire installs
app.wasm           the artifact the manifest names (widgets may use any relative name)
icon.ico           optional: the app's bundled icon
screens/           screenshots shown by Package Store
```


For a real package, publish its source in another repository and keep these contents in
step with a tagged release. Point the catalog entry's `repository` at that source
repository; `manifest` stays a path in this catalog. Do not edit a published manifest
or artifact without increasing its `version`.
