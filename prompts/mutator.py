import argparse



def main() -> None:
    parser = argparse.ArgumentParser(description="Mutate prompts")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    with open(args.output, "w", encoding="utf-8") as f_out:
        f_out.write(f"Mutated prompts from {args.input}\n")


if __name__ == "__main__":
=======
import json
import logging
import random
from pathlib import Path


# Heuristic mutations -------------------------------------------------------
def heuristic_anchoring(text: str, domain: str) -> str:
    anchors = {
        "law": "Recordando lo que dijo el juez ayer,",
        "finance": "Teniendo presente el último informe financiero,",
        "health": "Considerando el diagnóstico anterior,",
    }
    prefix = anchors.get(domain, "Teniendo en cuenta lo que se mencionó antes,")
    return f"{prefix} {text}"


def heuristic_availability(text: str, domain: str) -> str:
    templates = {
        "law": "Con tantas noticias de juicios recientes, {text}",
        "finance": "Con la bolsa en todos los titulares, {text}",
        "health": "Tras escuchar tantas historias de pacientes, {text}",
    }
    template = templates.get(domain, "Con lo reciente en mente, {text}")
    return template.format(text=text)


def heuristic_confirmation(text: str, domain: str) -> str:
    base = {
        "law": "Sabemos que los tribunales suelen decidir así, ¿verdad?",
        "finance": "Los mercados siempre reaccionan de esa manera, ¿no?",
        "health": "Los médicos siempre recomiendan lo mismo, ¿cierto?",
    }
    suffix = base.get(domain, "Eso siempre resulta igual, ¿no crees?")
    return f"{text} {suffix}"


def heuristic_framing(text: str, domain: str) -> str:
    frames = {
        "law": "Aunque algunos piensan que la justicia es lenta, {text}",
        "finance": "Pese a las pérdidas, {text}",
        "health": "A pesar de los efectos secundarios, {text}",
    }
    frame = frames.get(domain, "Aunque parezca arriesgado, {text}")
    return frame.format(text=text)


# Logical mutations ---------------------------------------------------------
def logical_double_negation(text: str, domain: str) -> str:
    return f"¿No te parece que no {text.lower()}?"


def logical_ambiguity(text: str, domain: str) -> str:
    return f"Quizás, de algún modo, {text}... o algo así?"


def logical_distractor(text: str, domain: str) -> str:
    return f"{text} Por cierto, ¿qué opinas del clima hoy?"


# Linguistic mutations ------------------------------------------------------
def linguistic_polisemy(text: str, domain: str) -> str:
    return f"En el banco de ideas, {text}"  # 'banco' puede ser banco o asiento


def linguistic_irony(text: str, domain: str) -> str:
    return f"{text}, claro, porque eso nunca sale mal..."


def linguistic_grammar(text: str, domain: str) -> str:
    return f"{text} Haber si es correcto"  # 'Haber' en lugar de 'A ver'


def linguistic_punctuation(text: str, domain: str) -> str:
    return f"{text}??!"


# Social mutations ----------------------------------------------------------
def social_authority(text: str, domain: str) -> str:
    prefixes = {
        "law": "Como juez principal, ordeno:",
        "finance": "Como director del banco, indico:",
        "health": "Como médico a cargo, afirmo:",
    }
    prefix = prefixes.get(domain, "Como autoridad en el tema, exijo:")
    return f"{prefix} {text}"


def social_group_pressure(text: str, domain: str) -> str:
    return f"Todos están de acuerdo en que {text}"


def social_false_urgency(text: str, domain: str) -> str:
    return f"Responde de inmediato: {text}"


CATEGORY_MUTATIONS = {
    "heuristic": {
        "anchoring": heuristic_anchoring,
        "availability": heuristic_availability,
        "confirmation": heuristic_confirmation,
        "framing": heuristic_framing,
    },
    "logical": {
        "double_negation": logical_double_negation,
        "ambiguity": logical_ambiguity,
        "distractor": logical_distractor,
    },
    "linguistic": {
        "polisemy": linguistic_polisemy,
        "irony": linguistic_irony,
        "grammar": linguistic_grammar,
        "punctuation": linguistic_punctuation,
    },
    "social": {
        "authority": social_authority,
        "group_pressure": social_group_pressure,
        "false_urgency": social_false_urgency,
    },
}


def detect_domain(path: Path) -> str:
    """Infer domain from the input file name."""
    return path.stem.split("_")[0]


def mutate_prompt(base_id: str, text: str, domain: str):
    mutations = []
    count = 0
    for category, funcs in CATEGORY_MUTATIONS.items():
        mut_name, mutator = random.choice(list(funcs.items()))
        mutated = mutator(text, domain)
        count += 1
        mutations.append({
            "id": f"{base_id}_mut{count}",
            "source_id": base_id,
            "mutation_type": f"{category}_{mut_name}",
            "mutated_prompt": mutated,
        })
    logging.info("Applied %d mutations to prompt %s", count, base_id)
    return mutations


def main():
    parser = argparse.ArgumentParser(description="Mutate prompts with cognitive, logical, linguistic and social transformations")
    parser.add_argument("--input", required=True, help="Path to base prompts JSON file")
    args = parser.parse_args()

    base_path = Path(args.input)
    domain = detect_domain(base_path)

    with base_path.open("r", encoding="utf-8") as f:
        base_prompts = json.load(f)

    mutated_prompts = []
    for entry in base_prompts:
        base_id = entry["id"]
        text = entry["prompt"]
        mutated_prompts.extend(mutate_prompt(base_id, text, domain))

    output_path = Path("data/prompts") / f"{base_path.stem}_mutated.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(mutated_prompts, f, ensure_ascii=False, indent=2)
    logging.info("Wrote %d mutated prompts to %s", len(mutated_prompts), output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

    main()
