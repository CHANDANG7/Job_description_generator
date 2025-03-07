def job_description_prompt(role_name, role_requirements, company_values):
    return (
        f"Generate a **concise, structured job description** in **2-3 paragraphs** for the role below:\n\n"
        f"**Role:** {role_name}\n"
        f"**Company Values:** {company_values}\n\n"
        "Ensure the description is engaging and well-formatted. Include:\n"
        "- An introduction with a brief role overview.\n"
        "- **Key Responsibilities** in bullet points.\n"
        "- **Requirements** in bullet points.\n"
        "- **Benefits** in bullet points.\n\n"
        "Make the job description clear, professional, and appealing."
    )
