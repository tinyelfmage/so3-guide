import re


def alpha_filter(string):
    filtered = string.replace(" ", "_").lower()
    filtered = re.sub(r"\W+", "", filtered)
    return filtered


def replace(match):
    match = match.group(0)
    url = alpha_filter(match)
    return "<a href='#{0}'>{1}</a>".format(url, match[1:-1])


word_count = 0
header = []
output = []
table_of_contents = []

with open("so3_guide_header.html") as h:
    lines = h.readlines()
    for line in lines:
        header.append(line[:-1])

header.append('<div class="body" id="body">')
table_of_contents.append("<div class='toc'>")
table_of_contents.append("<big><b>Table of Contents</b></big>")

with open("source.txt") as f:
    lines = f.readlines()
    current_level = 0
    bullet_open = False

    for line in lines:
        line = line.strip()
        if line:
            prefix = line.split("#")[0]
            content = line.split("#")[1:]

            tab = "" if current_level == 0 else "  " * current_level

            regex = re.compile(r"{[^{}]+}")
            line = regex.sub(replace, line)

            # manual closing tag for simplicity
            if line.startswith("##"):
                output.append(tab + "</div>")
                current_level -= 1

            # map display
            # map#IMG_NAME
            # [right-aligned text]
            # pam#
            elif prefix == "map":
                map_img = "./maps/%s.png" % content[0]
                items_img = "./maps/%s_items.png" % content[0]
                output.append(tab + "<div class='pair'><div class='overlay'>" +
                              ("<img src='%s'>" % map_img) +
                              ("<img src='%s' class='items'>" % items_img) +
                              "</div><div class='caption'>")
            elif prefix == "pam":
                output.append(tab + "</div></div>")

            # private action
            # paN#CHARACTER#content or
            # paN#all#sop,cli,mar,nel,rog,alb,pep,mir,adr#
            elif prefix[:2] == "pa":
                word_count += len(content[-1].split(" "))
                if content[0] == "*":
                    output.append(tab + "<div class='pa' " +
                                  "char='girlboy,cliff,sophia,maria,nel,roger,albel,peppita,mirage,adray'><p>" +
                                  "<b>PA {0}:</b> {1}</p></div>".format(prefix[2:], content[-1]))
                if content[0] == "all":
                    output.append(tab + "<div class='pa' char='all'><p><b>PA %s:</b> not yet implemented</p></div>" % prefix[2:])
                else:
                    output.append(tab + "<div class='pa' char='{1}'><p><b>PA {0}:</b> {2}</p></div>".format(prefix[2:], *content))

            # toggle line
            # tog#TYPE#content
            elif prefix == "tog":
                word_count += len(content[-1].split(" "))

                if content[0] == "encyclopedia":
                    output.append(tab + "<p class='%s'><b>Dictionary entry:</b> %s</p>" % tuple(content))
                else:
                    output.append(tab + "<p class='%s'>%s</p>" % tuple(content))

            # TODO: sections that can be open/closed on their own
            # sec#type#title
            # [content]
            # ces#
            elif prefix == "sec":
                tag = content[0] + "_" + alpha_filter(content[-1])
                output.append(tab + "<div class='panel-group'><div class='panel panel-default'>" +
                              "<div class='panel-heading'><h4 class='panel-title'><b>" +
                              "<a data-toggle='collapse' href='#{0}'>{1}</a></b></h4></div>".format(tag, content[-1]) +
                              "<div id='%s' class='panel-collapse collapse'><div class='panel-body'>" % tag)
            elif prefix == "ces":
                output.append("</div></div></div></div>")

            # header + collapse
            # hN#title
            elif prefix[0] == "h":
                tag = "h_" + alpha_filter(content[0])
                output.append(tab + "<{0}><a href='#{1}' data-toggle='collapse'>{2}</a></{0}>".format(prefix, tag, content[0]))
                output.append(tab + "<div id='{}' class='collapse in'>".format(tag))

                if prefix[-1] == "1":
                    table_of_contents.append("<br><b><big><a href='#{0}'>{1}</a></big></b>".format(tag, content[0]))
                elif prefix[-1] == "2":
                    table_of_contents.append("<br>&nbsp;<b><a href='#{0}'>{1}</a></b>".format(tag, content[0]))
                else:
                    table_of_contents.append(" | <a href='#{0}'>{1}</a>".format(tag, content[0]))

                current_level = int(prefix[-1])

            # auto open/close bullet points
            # use -- to close
            elif line[0] == "-":
                word_count += len(line.split(" "))
                if line[1] == "-":
                    output.append(tab + "</ul>")
                    bullet_open = False
                elif bullet_open:
                    output.append(tab + "  <li>%s</li>" % line[1:])
                else:
                    output.append(tab + "<ul><li>%s</li>" % line[1:])
                    bullet_open = True

            # FOR DURING DEV ONLY:
            # ! at beginning of line to state something is missing aka it's a TODO
            elif line[0] == "!":
                output.append('<div class="panel panel-danger"><div class="panel-heading">' +
                              line[1:] + "</div></div>")
            elif line.startswith("TODO"):
                pass

            # consider this line to be full-on code already
            elif line[0] == "<":
                word_count += len(line.split(" "))
                output.append(tab + line)
            # normal line
            else:
                if line[0] == "/": line = line[1:]
                word_count += len(line.split(" "))
                output.append(tab + "<p>%s</p>" % line)
        else:
            output.append("")

table_of_contents.append("</div>\n")
output.append("<p>Current word count: %d</p>" % word_count)
output.append("</div>\n")

with open("index.html", "w") as text_file:
    text_file.write("\n".join(header))
    text_file.write("".join(table_of_contents))
    text_file.write("\n".join(output))
