# Source code inspired by https://github.com/ufal/nametag3/tree/main

import random
import urllib.error
import urllib.request
import json
import random
import sys


MAP = {"P": "PER", # e.g., Jimi Hendrix (en), Stanislav Procházka (cs)
       "pc": "MISC", # e.g., American (en), Němec (cs)
       "pf": "PER", # e.g., Jim (en), Stanislav (cs)
       "pp": "PER", # e.g., God (en), svatý Václav (cs)
       "pm": "PER", # e.g., Franklin D. Roosevelt (en), J. Alfred Prufrock (cs)
       "ps": "PER", # e.g., Hendrix (en), Kafka (cs)
       "p_": "PER", # PER by majority vote of the other "p" labels
       "gh": "LOC", # e.g., Taiwan Strait (en), Atlantik (cs)
       "gq": "LOC", # e.g., Manhattan (en), Letňany (cs)
       "gs": "LOC", # e.g., Wall Streen (en), Mostecká ulice (cs)
       "gu": "LOC", # e.g., Brussels (en), Praha (cs)
       "gl": "LOC", # e.g., Northfield Mountains (en), Ural (cs)
       "gr": "LOC", # e.g., Golan Heights (en), Ostravsko (cs)
       "gt": "LOC", # e.g., Asia (en), Evropa (cs)
       "gc": "LOC", # e.g., Finland (en), Čína (cs)
       "g_": "LOC", # LOC by majority vote of the other "g" labels
       "ia": "MISC", # e.g., Grand Slam (en), Stanley Cup (cs)
       "if": "ORG", # e.g., Gazprom (en), Plzeňská banka (cs)
       "ic": "ORG", # e.g., Oklahoma State University (en), Královská akademie (cs)
       "io": "ORG", # e.g., NATO (en), KDU-ČSL (cs)
       "i_": "ORG", # ORG by majority vote of the other "i" labels
       "oa": "MISC", # e.g., Mission: Impossible (en), Nebezpečná rychlost (cs)
       "or": "MISC", # e.g., Regulation No. 2913/92 (en), Zákon o státní službě (cs)
       "op": "MISC", # e.g., Boeing (en), Opel (cs)
       "o_": "MISC", # e.g., BSD (en), HIV (cs)
       "ms": "ORG", # e.g., Israel Radio (en), Radio New Zealand (en), Radio Morava (cs)
       "mn": "ORG"} # e.g., The New York Times (en), The Times (en), Star Magazine (en), Wall Street Journal (en), Journal of Forensic Studies (cs)
UNMAPPED = ["T", # e.g., 1996-08-22 (en), 18. května (cs)
            "A", # not present in English data, Ministerstvo kultury, Maltézské náměstí, Praha 118 11 (cs)
            "C", # not present in English data, vs. some extremely long names of artistic products (cs)
            "pd", # e.g., Mr (en), Mgr. (cs)
            "om", # e.g., dollar (en), Kč (cs)
            "oe", # e.g., mm (en), kg (cs)
            "tf", # e.g., Christmas (en), Silvestr (cs)
            "ty", # e.g., 1983 (en), 1945 (cs)
            "tm", # e.g., April (en), květen (cs)
            "th", # e.g., 11.16 a.m. (en), 9.00 (cs)
            "td", # not present in English data, 26. (cs)
            "mi", # not present in English data, https:... (cs)
            "me", # derivatives@reuters.com (en), wise.desk@csob.cz (cs)
            "ah", # not present in English data, Na Perštýně 6 (cs)
            "az", # not present in English data, 118 11 (cs)
            "at", # not present in English data, 287 085 111 (cs)
            "nb", # not present in English data, 13 (cs)
            "ni", # e.g., 5. (en), 70. (cs)
            "ns", # e.g., 6-3 (en), 1:1 (cs)
            "nc", # e.g., 12 (en), 127 (cs)
            "no", # e.g., 11th (en), 17. (cs)
            "na", # e.g., 43-year-old (en), Řehák, 65. (cs)
            "n_"] # not present in English data, 7 (cs)


class EntityGenerator:
    SERVICE_URL = "https://lindat.mff.cuni.cz/services/nametag/api"
    MODEL = "nametag3-czech-cnec2.0-240830"

    def generate_entities(self, inp_data: str) -> list[dict]:
        inp_data = inp_data.upper()

        request_data = {
            "input": "untokenized",
            "output": "conll",
            "data": inp_data,
            "model": self.MODEL,
        }

        try:
            response = self.perform_request(self.SERVICE_URL, "recognize", request_data)
            if "model" not in response or "result" not in response:
                raise ValueError("Cannot parse the NameTag 3 'recognize' REST request response.")

            return self.group_conll_entities_to_dict(self.format_entities(response["result"].splitlines()))

        except Exception as e:
            return []

    def perform_request(self, server: str, method: str, params: dict):
        if not params:
            request_headers, request_data = {}, None
        else:
            boundary = "{:x}".format(random.getrandbits(50 * 4))
            request_headers = {"Content-Type": "multipart/form-data; boundary=\"{}\"".format(boundary)}
            request_data = []
            for name, value in params.items():
                request_data.extend([
                    "--" + boundary,
                    "Content-Disposition: form-data; name=\"{}\"".format(name),
                    "Content-Transfer-Encoding: 8bit",
                    "Content-Type: text/plain; charset=utf-8",
                    "",
                    value,
                ])
            request_data.extend(["--" + boundary + "--", ""])
            request_data = "\r\n".join(request_data).encode("utf-8")

        try:            
            with urllib.request.urlopen(urllib.request.Request(
                url="{}/{}".format(server, method), headers=request_headers, data=request_data
            )) as request:
                return json.loads(request.read())
        except urllib.error.HTTPError as e:
            print("An exception was raised during NameTag 3 'recognize' REST request.\n"
                "The service returned the following error:\n"
                "  {}".format(e.fp.read().decode("utf-8")), file=sys.stderr)
            raise
        except json.JSONDecodeError as e:
            print("Cannot parse the JSON response of NameTag 3 'recognize' REST request.\n"
                "  {}".format(e.msg), file=sys.stderr)
            raise
        
    def format_entities(self, extracted_entities: list[str]) -> list[str]:
        formatted_entities = []

        for line in extracted_entities:
            line = line.strip()

            if not line:
                continue

            cols = line.split("\t")

            if cols[1] != "O":
                label = cols[1].split("|")[0]
                form, ne_type = label.split("-")

                if ne_type in UNMAPPED:
                    cols[1] = "O"
                
                elif ne_type not in MAP:
                    continue
                
                else:
                    cols[1] = "-".join([form, MAP[ne_type]])

            if cols is not None:
                formatted_entities.append("\t".join(cols))
        
        return formatted_entities
    
    def group_conll_entities_to_dict(self, lines: list[str]) -> list[dict]:
        groups = []
        current_tokens = []
        current_label = None

        for item in lines:
            token, tag = item.split("\t")

            if tag.startswith("B-"):
                if current_tokens:
                    groups.append({
                        "type": current_label,
                        "value": " ".join(current_tokens)
                    })

                current_tokens = [token]
                current_label = tag[2:]

            elif tag.startswith("I-") and current_label == tag[2:]:
                current_tokens.append(token)

            else: 
                if current_tokens:
                    groups.append({
                        "type": current_label,
                        "value": " ".join(current_tokens)
                    })
                    current_tokens = []
                    current_label = None
                
        if current_tokens:
            groups.append({
                "type": current_label,
                "value": " ".join(current_tokens)
            })

        return groups
