import click
import chevron
import os
import json

from .Utils import Utils
from .SailorUtils import SailorUtils

class Sailor:

    def build(outdir, treasuredir):
        # click.echo(f"{outdir} : {treasuredir}.")

        if not os.path.exists(treasuredir):
            click.echo(f"cannot generate build treasure does not exist at {treasuredir}.")
            return 

        click.echo(f"building sailor...")
        
        # build tags
        htmlout = os.path.join(outdir, "Tags")
        Utils.checkAndCreate(htmlout)

        Sailor.buildTags(htmlout, treasuredir)

        # build units
        unitsout = os.path.join(outdir, "Units")
        Utils.checkAndCreate(unitsout)

        Sailor.buildUnits(unitsout, treasuredir)

        Sailor.buildLanguageUnits(unitsout, treasuredir)

        # build events
        eventsout = os.path.join(outdir, "Events")
        Utils.checkAndCreate(eventsout)

        Sailor.buildEvents(eventsout, treasuredir)

        # build event result map
        Sailor.buildEventResultMap(eventsout, treasuredir)

        # build attributes
        Sailor.buildGlobalAttributeGroup(outdir, treasuredir)

        # build tailwind
        # Sailor.buildTailwind(outdir, treasuredir)

        # todo: css properties
        Sailor.buildCSSProperties(outdir, treasuredir)

        # build DOM methods (element handles)
        methodsout = os.path.join(outdir, "Methods")
        Utils.checkAndCreate(methodsout)
        Sailor.buildMethods(methodsout, treasuredir)

        return
    
    def buildTags(outdir, treasuredir):
        # TODO: Utils.templates, Utils.tags
        tag_treasure = os.path.join(treasuredir, "tags.json")
        templateURL = os.path.join("Templates", 'Sailor', "HTML", "Tag.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)
        
        for tag, body in data.items():
            tag = tag.lower()

            description = body["description"]

            if "attributes" not in body:
                attributes = []
            else:
                attributes = SailorUtils.formatAttributes(body["attributes"])

            if tag in SailorUtils.excluded_tags:
                continue

            # if "alias" in body:
            #     ctag = body["alias"]
            # else:
            #     ctag = tag.capitalize()
            ctag = tag.capitalize()

            # def check_init(name):
            #     for init in body["inits"]:
            #         if name == init["type"]:
            #             return True
            #     return False

            # TODO: add this back in, removed for 0.2
            
            args = {
                "ctag": ctag,
                "tag": tag.lower(),
                "head": body["type"] == "head" if "type" in body else False,
                "description": description,
                "attributes": attributes,
                "inits": list(map(lambda v: {
                    "initRequired": v["type"] == "required",
                    "initRequiredWithBody": v["type"] == "required-with-body",
                    "initRequiredWithText": v["type"] == "required-with-text",
                    "initEmpty": v["type"] == "empty",
                    "initText": v["type"] == "text", # and not check_init("body")
                    "initBody": v["type"] == "body",
                    "args": Utils.createLastElementDictArray(list(map(lambda arg: SailorUtils.createArgs(arg), v["args"].items())) if "args" in v else [])
                }, body["inits"]))
            }

            # # add default inits for all tags
            # args["inits"] = list(filter(lambda v: v["initRequired"] or v["initRequiredWithBody"], args["inits"]))

            # args["inits"].append({
            #     "initRequired": False,
            #     "initRequiredWithBody": False,
            #     "initEmpty": True,
            #     "initText": False,
            #     "initBody":True,
            #     "args": False
            # })
            
            # print(args)
            out_url = os.path.join(outdir, f"HTML+{args['ctag']}.swift")

            Utils.build(templateURL, out_url, args)

        f.close()

    def buildTailwind(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "tailwind.json")
        templateURL = os.path.join("Templates", "Sailor", "Styling", "Tailwind+Classes.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        def convert_name(name):
            if name[0] == "-":
                name = "neg" + name[1:]
            name = name.replace(" ", "")
            name = name.replace("/", "v")
            name = name.replace("\n", "")
            name = name.replace(".", "")
            name = name.replace("*", "")
            name = name.replace("#", "")
            name = name.replace(":", "")
            name = name.replace("%", "Pct")
            return name

        classes = list(
            map(
                lambda v: {
                    "name": v[0].replace(".", ""),
                    "alias": Utils.switch_to_camel(convert_name(v[0].replace(".", ""))),
                    "description": v[1].replace("\n", ""),
                    "isPack": ":" in v[0],
                }, data.items()
            )
        )
        packables = list(
            filter(
                lambda v: ":" not in v["name"],
                map(
                    lambda v: {
                        "name": v[0].replace(".", ""),
                        "alias": Utils.switch_to_camel(convert_name(v[0].replace(".", ""))),
                        "description": v[1].replace("\n", ""),
                    }, data.items()
                )
            )
        )

        args = {
            "description": "Tailwind CSS classes supported on sailor.",
            "cases": classes,
            "packables": packables
        }

        out_url = os.path.join(outdir, "Tailwind+Classes.swift")
        Utils.build(templateURL, out_url, args)

    def buildGlobalAttributeGroup(outdir, treasuredir):
        # TODO: Utils.templates, Utils.tags
        tag_treasure = os.path.join(treasuredir, "global-attributes.json")
        templateURL = os.path.join("Templates", "Sailor", "HTML", "GlobalAttributeGroup.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        attributes = SailorUtils.formatAttributes(data)
        
        args = {
            "description": "Group of all global attributes, which are attributes that can be used with any HTML element.",
            "attributes": attributes,
        }

        out_url = os.path.join(outdir, "GlobalAttributeGroup.swift")
        Utils.build(templateURL, out_url, args)

    def buildPropUnits(outdir, treasuredir):
        unit_treasure = os.path.join(treasuredir, "units.json")
        # punit_treasure = os.path.join(treasuredir, "property_units.json")

        templateURL = os.path.join("Templates", 'Sailor', "HTML", "PropUnit+Units.mustache")
        # TODO:
        
    def buildUnits(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "units.json")
        templateURL = os.path.join("Templates", 'Sailor', "HTML", "Unit+Enum.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        def format_cases(body):
            cases_raw = body.get("cases", {})
            # Handle list-format cases: [{"name": swiftName, "value": cssValue}, ...]
            if isinstance(cases_raw, list):
                return [{
                    "name": item["value"],
                    "alias": item["name"],
                    "description": item.get("description", ""),
                    "args": [],
                    "hasAssociatedValue": False,
                    "isFormatted": False,
                    "format": "",
                    "last": False,
                } for item in cases_raw]
            return list(
                map(lambda v: {
                "name": SailorUtils.remove_case_id(v[0]),
                "alias": SailorUtils.remove_case_id(v[0]),
                "description": v[1]["description"],
                "args": [
                    {
                        "name": SailorUtils.formatName(name),
                        "value": SailorUtils.convert_type(value),
                        "isShown": isShown,
                    } for value, name, isShown in zip(
                        v[1]["values"] if "values" in v[1] else [],
                        v[1]["names"] if "names" in v[1] else [],
                        ([True] * len(v[1]["names"] if "names" in v[1] else []) if "showNames" in v[1] else
                        v[1]["shown"] if "shown" in v[1]
                        else [False] * len(v[1]["names"] if "names" in v[1] else [])),
                    )
                ],
                # "values": v[1]["values"] if "values" in v[1] else [],
                # "names": v[1]["names"] if "names" in v[1] else [],
                "hasAssociatedValue": "values" in v[1],
                "isFormatted": "format" in v[1],
                "format": SailorUtils.put_formatted(v[1]["format"], v[1].get("names", []), types=v[1].get("values", [])) if "format" in v[1] else "",
                "last": False
            }, cases_raw.items()))

        for name, body in data.items():
            description = body["description"]
            cname = Utils.capitalize_keep_upper(name)
            cases = format_cases(body)

            if "inherit" in body:
                for inherited_unit in body["inherit"]:
                    cases.extend(format_cases(data[inherited_unit]))

            for case in cases:
                case["alias"] = Utils.switch_to_camel(case["alias"])

                for arg in case["args"]: arg["last"] = False
                
                if len(case["args"]) > 0:
                    case["args"][-1]["last"] = True
                
                # case["values"] = list(map(lambda v: {"value": v, "last": False}, case["values"]))
                
                # if len(case["values"]) > 0:
                #     case["values"][-1]["last"] = True

            cases[-1]["last"] = True

            args = {
                "cname": cname,
                "cases": cases,
                "description": description
            }

            out_url = os.path.join(outdir, f"Unit+{cname}.swift")

            Utils.build(templateURL, out_url, args)

        f.close()

    def buildLanguageUnits(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "language-codes.json")
        templateURL = os.path.join("Templates", 'Sailor', "HTML", "Unit+Enum.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        # for name, code in data.items():
        description = "Language code for a specific language."
        cname = "Language"
        cases = list(
            map(lambda v: {
            "name": v[1],
            "alias": v[1],
            "description": f"language code for {v[0]}.",
            "values": [],
            "names": [],
            "hasAssociatedValue": False,
            "last": False
        }, data.items()))

        for case in cases:
            case["names"] = list(map(lambda v: {"value": v, "last": False}, case["names"]))
            if len(case["names"]) > 0:
                case["names"][-1]["last"] = True
            
            case["values"] = list(map(lambda v: {"value": v, "last": False}, case["values"]))
            
            if len(case["values"]) > 0:
                case["values"][-1]["last"] = True

        cases[-1]["last"] = True

        args = {
            "cname": cname,
            "cases": cases,
            "description": description
        }

        out_url = os.path.join(outdir, f"Unit+{cname}.swift")

        Utils.build(templateURL, out_url, args)

        f.close()

    def buildEvents(outdir, treasuredir):
        event_treasure = os.path.join(treasuredir, "events.json")
        global_template = os.path.join("Templates", "Sailor", "HTML", "EventGroup.mustache")
        targeted_template = os.path.join("Templates", "Sailor", "HTML", "TargetedEventGroup.mustache")

        f = open(event_treasure)
        data = json.load(f)

        # Map events.json data types to EventResult types
        type_map = {
            "string": {"ctype": "String", "ltype": "string"},
            "int": {"ctype": "Int", "ltype": "int"},
            "float": {"ctype": "Double", "ltype": "float"},
            "bool": {"ctype": "Bool", "ltype": "bool"},
        }

        def format_event(event_name, event_body):
            """Convert an events.json event entry into mustache template data."""
            cname = Utils.capitalize_keep_upper(event_name)

            has_data = event_body.get("data") is not None
            # Use the first data field as the typed value
            data_field = None
            data_key = None
            if has_data:
                data_key = next(iter(event_body["data"]))
                data_field = event_body["data"][data_key]

            # Event name uses "js_event:field" for typed events (so JSNode
            # can split on ":" — the part before ":" is the addEventListener
            # name, the full string is the resultMap key)
            js_event = event_body["js_event"]
            lname = f"{js_event}:{data_key}" if has_data else js_event

            result = {
                "name": cname,
                "lname": lname,
                "description": event_body["description"],
                "istyped": has_data,
            }

            if has_data and data_field:
                mapped = type_map.get(data_field["type"], {"ctype": "String", "ltype": "string"})
                result["ctype"] = mapped["ctype"]
                result["ltype"] = mapped["ltype"]

            return result

        # --- Build global events (one file with all global events on Element) ---
        global_events = []
        for event_name, event_body in data.get("global", {}).items():
            global_events.append(format_event(event_name, event_body))

        if global_events:
            args = {
                "groupName": "Element+GlobalEvents",
                "events": global_events,
            }
            out_url = os.path.join(outdir, "Element+GlobalEvents.swift")
            Utils.build(global_template, out_url, args)

        # --- Build targeted events (one file per tag) ---
        # Collect all events for each tag across all groups
        tag_events = {}
        for group_name, group_body in data.get("targeted", {}).items():
            tags = group_body.get("tags", [])
            events = group_body.get("events", {})

            for tag in tags:
                if tag not in tag_events:
                    tag_events[tag] = []
                for event_name, event_body in events.items():
                    tag_events[tag].append(format_event(event_name, event_body))

        for tag, events in tag_events.items():
            # Skip tags that are excluded from codegen
            if tag in SailorUtils.excluded_tags:
                continue

            ctag = tag.capitalize()
            args = {
                "ctag": ctag,
                "events": events,
            }
            out_url = os.path.join(outdir, f"HTML+{ctag}+Events.swift")
            Utils.build(targeted_template, out_url, args)

        f.close()

    def buildEventResultMap(outdir, treasuredir):
        event_treasure = os.path.join(treasuredir, "events.json")
        templateURL = os.path.join("Templates", "Sailor", "HTML", "EventResult+ResultMap.mustache")

        f = open(event_treasure)
        data = json.load(f)

        # Collect all events that have data fields (need extraction logic)
        events = []
        seen = set()

        for section in ["global", "targeted"]:
            section_data = data.get(section, {})
            if section == "global":
                items = section_data.items()
            else:
                items = []
                for group_body in section_data.values():
                    items.extend(group_body.get("events", {}).items())

            for event_name, event_body in items:
                js_event = event_body["js_event"]
                if js_event in seen:
                    continue
                if event_body.get("data") is None:
                    continue

                seen.add(js_event)
                first_key = next(iter(event_body["data"]))
                field = event_body["data"][first_key]

                # Map data type to JSValue accessor
                js_accessor_map = {
                    "string": "string",
                    "int": "number",
                    "float": "number",
                    "bool": "boolean",
                }

                # Map data type to EventResult case
                result_type_map = {
                    "string": "string",
                    "int": "int",
                    "float": "float",
                    "bool": "bool",
                }

                events.append({
                    "name": f"{js_event}:{first_key}",
                    "path": field["path"],
                    "js_accessor": js_accessor_map.get(field["type"], "string"),
                    "result_type": result_type_map.get(field["type"], "string"),
                    "last": False,
                })

        if events:
            events[-1]["last"] = True

            args = {"events": events}
            out_url = os.path.join(outdir, "EventResult+ResultMap.swift")
            Utils.build(templateURL, out_url, args)

        f.close()


    def buildCSSProperties(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "properties.json")
        # tag_global_props = os.path.join(treasuredir, "global-property-cases.json")

        templateURL = os.path.join("Templates", 'Sailor', "Styling", "Style+Property.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        completed = set()

        # fg = open(tag_global_props)
        # global_data = json.load(fg)

        args = {
            "properties": []
        }

        for name, body in data.items():
            name = name.split(":")[0]
            params = []

            if "*" in name:
                name = name[:-2]

                for label, body in body.items():
                    label = label.split(":")[0]
                    params.append((label, body))
            else:
                params = [("", body)]
            
            for param in params:
                # if param[0] != "":
                #     print(param[0])
                body = param[1]
                formatted_names = [SailorUtils.check_keyword_name(name) for name in body["names"]]
                is_param = param[0] != "" 
                is_shorthand = "shorthand" in body and body["shorthand"]
                shown_params = is_param or is_shorthand
                converted_types = [SailorUtils.convert_type(t) for t in body["types"]]
                if is_param:
                    full_name = name + "-" + param[0]
                    if "alias" in body:
                        full_name = body["alias"]
                else:
                    full_name = name

                # normal initializers
                if body["names"] != []:
                    args["properties"].append({
                        "name": full_name,
                        "shownParams": shown_params,
                        "isShorthand": is_shorthand,
                        "alias": SailorUtils.check_keyword_name(Utils.switch_to_camel(name)),
                        "typedNames": [ {"tname": tname, "type": tvalue, "last": False} for tname, tvalue in zip(formatted_names, converted_types) ],
                        "formatted": SailorUtils.put_formatted(body["format"], body["names"], formatted_names, body["types"]),
                        "description": body["description"]
                    })
                    
                    args["properties"][-1]["typedNames"][-1]["last"] = True

                # global params initializer (skip if property already uses Unit.Global)
                if name not in completed and not (len(body["types"]) == 1 and body["types"][0] == "Unit.Global"):
                    #typeName = "globalValue" if param[0] == "" else param[0]
                    typeName = "globalValue"

                    completed.add(name)
                    args["properties"].append({
                        "name": name,
                        "shownParams": False, # shown_params
                        "isShorthand": False,
                        "alias": SailorUtils.check_keyword_name(Utils.switch_to_camel(name)),
                        "typedNames": [ {"tname": typeName, "type": "Unit.Global", "last": True } ],
                        "formatted": SailorUtils.put_formatted("{{" + typeName + "}}", [typeName]),
                        "description": body["description"]
                    })

        out_url = os.path.join(outdir, f"CSS+Properties.swift")

        Utils.build(templateURL, out_url, args)

        f.close()
        # fg.close()

    def buildMethods(outdir, treasuredir):
        """Generate typed element handle types from methods.json.

        Produces:
        - ElementHandle.swift — base handle with HTMLElement methods
        - <Tag>Handle.swift — per-tag handles with inherited + specific methods
        - Element+Handle.swift — .handle computed property on Element
        - HTML+<Tag>+Handle.swift — .handle typed property per tag
        """
        methods_treasure = os.path.join(treasuredir, "methods.json")
        if not os.path.exists(methods_treasure):
            click.echo("  skipping methods (no methods.json)")
            return

        f = open(methods_treasure)
        data = json.load(f)
        f.close()

        interfaces = data.get("interfaces", {})
        tag_map = data.get("tag_interface_map", {})

        return_cast_map = {
            "Bool": "result.boolean",
            "String": "result.string",
            "Int": "Int(result.number)",
            "Double": "Double(result.number)",
        }

        def swift_param_sig(param):
            """Generate Swift parameter signature."""
            name = param["name"]
            ptype = param["type"]
            if param.get("optional", False):
                default = param.get("default", "nil")
                ptype_opt = f"{ptype}?" if "nil" == default else ptype
                return f"{name}: {ptype_opt} = {default}"
            return f"{name}: {ptype}"

        def swift_js_arg(param):
            """Generate JS argument for a method call."""
            name = param["name"]
            js_type = param.get("js_type", "string")
            js_transform = param.get("js_transform")
            if js_transform:
                return js_transform.replace("value", name)
            if js_type == "number":
                return name
            if js_type == "string":
                return name
            return name

        def generate_method_swift(method_name, method_body, indent="    "):
            """Generate a Swift method from a methods.json entry."""
            lines = []
            js_method = method_body["js_method"]
            params = method_body.get("params", [])
            returns = method_body.get("returns")
            desc = method_body["description"]

            lines.append(f"{indent}/// {desc}")

            # Build signature
            if params:
                param_strs = [swift_param_sig(p) for p in params]
                sig = ", ".join(param_strs)
                lines.append(f"{indent}@MainActor public func {method_name}({sig}) {{")
                lines.append(f"{indent}    #if os(WASI)")
                # Build JS call args
                js_args = ", ".join([swift_js_arg(p) for p in params])
                lines.append(f"{indent}    _ = jsValue?.{js_method}({js_args})")
                lines.append(f"{indent}    #endif")
                lines.append(f"{indent}}}")
            elif returns:
                cast = return_cast_map.get(returns, "result.string")
                lines.append(f"{indent}@discardableResult")
                lines.append(f"{indent}@MainActor public func {method_name}() -> {returns}? {{")
                lines.append(f"{indent}    #if os(WASI)")
                lines.append(f"{indent}    guard let result = jsValue?.{js_method}() else {{ return nil }}")
                lines.append(f"{indent}    return {cast}")
                lines.append(f"{indent}    #else")
                lines.append(f"{indent}    return nil")
                lines.append(f"{indent}    #endif")
                lines.append(f"{indent}}}")
            else:
                lines.append(f"{indent}@MainActor public func {method_name}() {{")
                lines.append(f"{indent}    #if os(WASI)")
                lines.append(f"{indent}    _ = jsValue?.{js_method}()")
                lines.append(f"{indent}    #endif")
                lines.append(f"{indent}}}")

            lines.append("")
            return "\n".join(lines)

        def generate_delegation(method_name, method_body, indent="    "):
            """Generate a method that delegates to base.method()."""
            lines = []
            params = method_body.get("params", [])
            returns = method_body.get("returns")
            desc = method_body["description"]

            lines.append(f"{indent}/// {desc}")

            if params:
                param_strs = [swift_param_sig(p) for p in params]
                sig = ", ".join(param_strs)
                call_args = ", ".join([f"{p['name']}: {p['name']}" for p in params])
                lines.append(f"{indent}@MainActor public func {method_name}({sig}) {{")
                lines.append(f"{indent}    base.{method_name}({call_args})")
                lines.append(f"{indent}}}")
            elif returns:
                lines.append(f"{indent}@discardableResult")
                lines.append(f"{indent}@MainActor public func {method_name}() -> {returns}? {{ base.{method_name}() }}")
            else:
                lines.append(f"{indent}@MainActor public func {method_name}() {{ base.{method_name}() }}")

            lines.append("")
            return "\n".join(lines)

        # ---- 1. Generate ElementHandle.swift (base HTMLElement methods) ----
        base_methods = interfaces.get("HTMLElement", {}).get("methods", {})

        element_handle_lines = [
            "// This file was autogenerated by Shipwright. DO NOT CHANGE.",
            "//",
            "//  ElementHandle.swift",
            "//",
            "",
            "import Sailboat",
            "",
            "#if os(WASI)",
            "@_spi(Private) import SailorWeb",
            "import JavaScriptKit",
            "#endif",
            "",
            "/// Typed element handle for calling DOM methods on any HTML element.",
            "/// Wraps the underlying renderer and provides type-safe method calls.",
            "public struct ElementHandle {",
            "    @_spi(Private) public let renderer: any Renderable",
            "",
            "    public init(_ renderer: any Renderable) {",
            "        self.renderer = renderer",
            "    }",
            "",
            "    #if os(WASI)",
            "    /// Access the underlying JSValue for direct method calls",
            "    @MainActor internal var jsValue: JSValue? {",
            "        (renderer as? JSNode).map { JSValue.object($0.element) }",
            "    }",
            "    #endif",
            "}",
            "",
            "// MARK: - Base HTMLElement methods (available on all elements)",
            "",
            "extension ElementHandle {",
        ]

        for method_name, method_body in base_methods.items():
            element_handle_lines.append(generate_method_swift(method_name, method_body))

        element_handle_lines.append("}")

        out_url = os.path.join(outdir, "ElementHandle.swift")
        of = open(out_url, "w")
        of.write("\n".join(element_handle_lines))
        of.close()

        # ---- 2. Generate per-tag handles ----
        for tag, interface_name in tag_map.items():
            if tag in SailorUtils.excluded_tags:
                continue

            interface = interfaces.get(interface_name, {})
            tag_methods = interface.get("methods", {})
            ctag = tag.capitalize()

            # Collect inherited base methods for delegation
            inherited = interfaces.get("HTMLElement", {}).get("methods", {})

            # Also check if this interface inherits from another non-HTMLElement
            parent = interface.get("inherits")
            parent_methods = {}
            if parent and parent != "HTMLElement":
                parent_methods = interfaces.get(parent, {}).get("methods", {})

            tag_handle_lines = [
                "// This file was autogenerated by Shipwright. DO NOT CHANGE.",
                "//",
                f"//  {ctag}Handle.swift",
                "//",
                "",
                "import Sailboat",
                "",
                "#if os(WASI)",
                "@_spi(Private) import SailorWeb",
                "import JavaScriptKit",
                "#endif",
                "",
                f"/// Typed element handle for {ctag} — includes tag-specific DOM methods.",
                f"public struct {ctag}Handle {{",
                "    @_spi(Private) public let base: ElementHandle",
                "",
                "    public init(_ renderer: any Renderable) {",
                "        self.base = ElementHandle(renderer)",
                "    }",
                "",
                "    #if os(WASI)",
                "    @MainActor internal var jsValue: JSValue? { base.jsValue }",
                "    #endif",
                "}",
                "",
                f"// MARK: - Inherited HTMLElement methods",
                "",
                f"extension {ctag}Handle {{",
            ]

            for method_name, method_body in inherited.items():
                tag_handle_lines.append(generate_delegation(method_name, method_body))

            tag_handle_lines.append("}")
            tag_handle_lines.append("")
            tag_handle_lines.append(f"// MARK: - {ctag}-specific methods")
            tag_handle_lines.append("")
            tag_handle_lines.append(f"extension {ctag}Handle {{")

            for method_name, method_body in tag_methods.items():
                tag_handle_lines.append(generate_method_swift(method_name, method_body))

            tag_handle_lines.append("}")

            out_url = os.path.join(outdir, f"{ctag}Handle.swift")
            of = open(out_url, "w")
            of.write("\n".join(tag_handle_lines))
            of.close()

        # ---- 3. Generate Element+Handle.swift (base .handle property) ----
        handle_ext_lines = [
            "// This file was autogenerated by Shipwright. DO NOT CHANGE.",
            "//",
            "//  Element+Handle.swift",
            "//",
            "",
            "import Sailboat",
            "",
            "extension Element {",
            "    /// Access the underlying DOM element handle for imperative method calls.",
            "    /// Use this in lifecycle closures like `.onAppear` to call DOM methods.",
            "    public var handle: ElementHandle {",
            "        ElementHandle(self.renderer)",
            "    }",
            "}",
        ]

        out_url = os.path.join(outdir, "Element+Handle.swift")
        of = open(out_url, "w")
        of.write("\n".join(handle_ext_lines))
        of.close()

        # ---- 4. Generate per-tag .handle overrides ----
        for tag, interface_name in tag_map.items():
            if tag in SailorUtils.excluded_tags:
                continue
            ctag = tag.capitalize()

            tag_ext_lines = [
                "// This file was autogenerated by Shipwright. DO NOT CHANGE.",
                "//",
                f"//  HTML+{ctag}+Handle.swift",
                "//",
                "",
                "import Sailboat",
                "",
                f"extension HTML.{ctag} {{",
                f"    /// Access the typed {ctag} DOM element handle for imperative method calls.",
                f"    public var {tag}Handle: {ctag}Handle {{",
                f"        {ctag}Handle(self.renderer)",
                "    }",
                "}",
            ]

            out_url = os.path.join(outdir, f"HTML+{ctag}+Handle.swift")
            of = open(out_url, "w")
            of.write("\n".join(tag_ext_lines))
            of.close()

        click.echo(f"  built {len(tag_map) + 1} element handles")