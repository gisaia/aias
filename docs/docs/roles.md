# Roles configuration

ARLAS allows the configuration of roles with permissions. Most of permissions are access rules that define a URL path with the allowd HTTP verbs.

A rule is a an expression composed of three parts seperated with the character `:` :
- the `r` prefix for declaringt the expression as a rule (`h` is for declaring a header)
- the path as a pattern (e.g. `/shop/.*)
- a comma seperated list of HTTP verbs

For instance, the following line is the rule for allowing `GET` and `DELETE` on any path starting with `/aproc/jobs/`:

```yaml
    - r:/aproc/jobs/.*:GET,DELETE
```

A role is defined with:

- a role name
- a description
- a list of permissions

Note: the role name must start with `role/arlas/` in order to be taken into account by ARLAS.

Example:

```yaml
  role/arlas/downloader:
    description:
    - "Can interact with the download API: Describe download process, launch download processes, get and delete a task status."
    permissions:
    - r:/aproc/processes/download:GET
    - r:/aproc/processes/download/execution:POST
    - r:/aproc/jobs/.*:GET,DELETE
```
