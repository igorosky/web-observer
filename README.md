# Web Observer

## Reqest flowchart
```mermaid
flowchart TD
    Start@{shape: circle} --> Request
    Request[Request URL] --> Check_respose
    Check_respose[Check response code] --> Get_element
    Get_element{{Get element}} --> Substitute_images{{Substitute images with its SHA256}}
    Substitute_images --> SHA256{{SHA256}}
    SHA256 --> Store{{Store state}}
    Store --> Web_view{{Generate web view}}
```

## Future ideas:
 - Analyse JSON responses
 - Analyze images as responses
 - Make a way to add some steps before the request (e.g. login)
 - Add a way to use different methods (e.g. POST, PUT, DELETE)
