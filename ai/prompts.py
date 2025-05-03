def build_portfolio_prompt(portfolio):
    if not portfolio:
        return "The portfolio is empty."

    lines = [f"- {item['symbol']} ({item['type']}): ${item['sum']}" for item in portfolio]
    joined = "\n".join(lines)
    return (
        "You are a financial AI assistant. Analyze the following portfolio:\n\n"
        f"{joined}\n\n"
        "Provide:\n"
        "1. A summary of its structure and concentration\n"
        "2. Suggestions for balancing or diversification\n"
        "3. Optional comments on individual assets if relevant"
    )
