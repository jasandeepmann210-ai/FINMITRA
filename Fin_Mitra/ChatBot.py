import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from rapidfuzz import fuzz

QUESTION_BANK = {
    "en": [
        {
            "id": "Q1",
            "question": "What is a tax audit for a school?",
            "answer": "A tax audit is an examination of the school’s books of accounts by a Chartered Accountant to ensure compliance with the Income Tax Act, 1961."
        },
        {
            "id": "Q2",
            "question": "Is tax audit mandatory for all schools?",
            "answer": "No. Tax audit is mandatory only when certain conditions related to income, registration, and turnover/gross receipts are met."
        },
        {
    "id": "Q3",
    "question": "When is a school required to undergo tax audit under Section 44AB?",
    "answer": html.Div([
        html.Div("A school must undergo tax audit under Section 44AB if:"),
        html.Ul([
            html.Li("It has taxable income"),
            html.Li("Its gross receipts exceed ₹1 crore in a financial year"),
        ])
    ])
}
,
        {
    "id": "Q4",
    "question": "Does a school registered under Section 12AB require a tax audit?",
    "answer": html.Div([
        html.Ul([
            html.Li("Not required, if the school applies 85% or more of its income for educational purposes and follows all exemption conditions."),
            html.Li("Required, if the school violates exemption conditions, has taxable income, or carries out commercial activities."),
        ])
    ])
}
,
        {
            "id": "Q5",
            "question": "What audit is applicable to schools registered under Section 12AB?",
            "answer": "Such schools are generally required to get their accounts audited and file Form 10B (charitable audit)."
        },
        {
            "id": "Q6",
            "question": "What happens if a school registered under Section 12AB earns taxable income?",
            "answer": "If taxable income arises and gross receipts exceed the prescribed limit, tax audit under Section 44AB becomes mandatory."
        },
        {
            "id": "Q7",
            "question": "Is tax audit compulsory for schools not registered under Section 12AB?",
            "answer": "Yes. If such a school’s gross receipts exceed ₹1 crore, tax audit under Section 44AB is compulsory."
        },
        {
            "id": "Q8",
            "question": "Are schools claiming exemption under Section 10(23C) required to get audit done?",
            "answer": "Yes. Schools approved under Section 10(23C) must get their accounts audited every year, irrespective of income limits."
        },
        {
    "id": "Q9",
    "question": "Is audit mandatory even if the school has no taxable income?",
    "answer": html.Div([
        html.Ul([
            html.Li("For 12AB and 10(23C) schools, audit may still be mandatory as per exemption conditions."),
            html.Li("For normal schools, audit is generally not required if there is no taxable income and turnover is within prescribed limits."),
        ])
    ])
}
,
        {
    "id": "Q10",
    "question": "Which audit forms are applicable to schools?",
    "answer": html.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("Type of School"),
                    html.Th("Applicable Audit Form"),
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td("Normal taxable school"),
                    html.Td("Form 3CA / 3CB & 3CD"),
                ]),
                html.Tr([
                    html.Td("12AB registered school"),
                    html.Td("Form 10B"),
                ]),
                html.Tr([
                    html.Td("10(23C) approved school"),
                    html.Td("Prescribed audit report"),
                ]),
            ]),
        ],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "fontSize": "13px",
        },
    )
}
,
        {
    "id": "Q11",
    "question": "What is the due date for tax audit of schools?",
    "answer": html.Div([
        html.Ul([
            html.Li("Audit report due date: 30th September"),
            html.Li("ITR filing due date: 31st October"),
        ]),
        html.Div(
            "(Subject to changes by the Income Tax Department)",
            style={"fontSize": "12px", "color": "#666", "marginTop": "4px"}
        )
    ])
}
,
        {
    "id": "Q12",
    "question": "What are the consequences of not conducting a tax audit?",
    "answer": html.Div([
        html.Div("Non-compliance may result in:"),
        html.Ul([
            html.Li("Penalty under Section 271B – 0.5% of turnover (maximum ₹1.5 lakh)"),
            html.Li("Cancellation of tax exemption"),
            html.Li("Income tax scrutiny and legal action"),
        ])
    ])
}
,
        {
            "id": "Q13",
            "question": "Does receiving foreign contributions make tax audit compulsory?",
            "answer": "Yes. In certain cases, receiving foreign contributions or being covered under other laws can make audit compulsory."
        },
        {
            "id": "Q14",
            "question": "Can the Income Tax Department order a special audit for a school?",
            "answer": "Yes. The Income Tax Department has the power to direct a special audit if required."
        },
        {
            "id": "Q15",
            "question": "What is the simplest rule to determine tax audit applicability for schools?",
            "answer": "If a school has taxable income and gross receipts exceed ₹1 crore, or if audit is required under exemption provisions (12AB or 10(23C)), tax audit is mandatory."
        },
        {
        "id": "Q16",
        "question": "What is Income Tax compliance for schools?",
        "answer": html.Div(
            "Income Tax compliance for schools means following all rules under the Income Tax Act, such as deducting and depositing TDS, filing returns, issuing certificates, maintaining records, and responding to tax notices."
        )
    },
    {
        "id": "Q17",
        "question": "Is a school required to deduct TDS on salaries?",
        "answer": html.Div(
            "Yes. Schools must deduct TDS under Section 192 on salaries paid to teaching and non-teaching staff if income exceeds the basic exemption limit."
        )
    },
    {
        "id": "Q18",
        "question": "On which other payments should schools deduct TDS?",
        "answer": html.Div([
            html.Div("TDS must be deducted on:"),
            html.Ul([
                html.Li("Contractor payments (Section 194C)"),
                html.Li("Professional fees (Section 194J)"),
                html.Li("Rent payments (Section 194I)"),
                html.Li("Other applicable services as per Income Tax Act"),
            ])
        ])
    },
    {
        "id": "Q19",
        "question": "What happens if TDS is not deducted or deposited on time?",
        "answer": html.Div(
            "Delay or failure results in interest, penalties, and late fees, and may also invite scrutiny from the Income Tax Department."
        )
    },
    {
        "id": "Q20",
        "question": "Which TDS returns must a school file?",
        "answer": html.Div([
            html.Ul([
                html.Li("Form 24Q – for salary payments"),
                html.Li("Form 26Q – for non-salary payments"),
            ]),
            html.Div(
                "These must be filed quarterly.",
                style={"marginTop": "4px"}
            )
        ])
    },
    {
        "id": "Q21",
        "question": "What is Form 16 and when should it be issued?",
        "answer": html.Div(
            "Form 16 is a TDS certificate for salary. It must be issued annually to employees after filing TDS returns."
        )
    },
    {
        "id": "Q22",
        "question": "What is Form 16A?",
        "answer": html.Div(
            "Form 16A is a TDS certificate for non-salary payments, issued quarterly to vendors and professionals."
        )
    },
    {
        "id": "Q23",
        "question": "Is a school required to file an Income Tax Return?",
        "answer": html.Div(
            "Yes. Every school must file an Income Tax Return (ITR), even if income is exempt."
        )
    },
    {
        "id": "Q24",
        "question": "How can a school claim income tax exemption?",
        "answer": html.Div(
            "A school can claim exemption by being registered under Section 12AB and complying with prescribed conditions."
        )
    },
    {
        "id": "Q25",
        "question": "What books and records should a school maintain?",
        "answer": html.Div([
            html.Div("Schools must maintain:"),
            html.Ul([
                html.Li("Salary and attendance registers"),
                html.Li("Payment vouchers and receipts"),
                html.Li("TDS records"),
                html.Li("Financial statements and audit reports"),
            ])
        ])
    },
    {
        "id": "Q26",
        "question": "Is a tax audit mandatory for schools?",
        "answer": html.Div(
            "A tax audit is required if the school meets the audit criteria under the Income Tax Act or as per exemption conditions."
        )
    },
    {
        "id": "Q27",
        "question": "What are PAN and TAN, and are they mandatory?",
        "answer": html.Div([
            html.Ul([
                html.Li("PAN (Permanent Account Number) identifies the school for tax purposes."),
                html.Li("TAN (Tax Deduction and Collection Account Number) is mandatory for TDS-related activities."),
            ])
        ])
    },
    {
        "id": "Q28",
        "question": "What should a school do if it receives an Income Tax notice?",
        "answer": html.Div(
            "The school must respond within the given time, provide required documents, and ensure compliance to avoid penalties."
        )
    },
    {
        "id": "Q29",
        "question": "Are schools required to pay advance tax?",
        "answer": html.Div(
            "Yes, if the school has taxable income, advance tax must be paid as per applicable rules."
        )
    },
    {
        "id": "Q30",
        "question": "What are the consequences of non-compliance?",
        "answer": html.Div([
            html.Div("Non-compliance may lead to:"),
            html.Ul([
                html.Li("Penalties and interest"),
                html.Li("Disallowance of exemptions"),
                html.Li("Legal action by the Income Tax Department"),
            ])
        ])
    },
     # ---------- Section A: 12AA Registration (Income Tax Exemption) ----------
    {
        "id": "Q31",
        "question": "What is 12AA registration for a school?",
        "answer": html.Div(
            "12AA registration is the Income Tax Department’s approval that allows a charitable trust or society (like a school) to claim income tax exemption under Sections 11 & 12 of the Income Tax Act."
        )
    },
    {
        "id": "Q32",
        "question": "When should a school apply for 12AA registration?",
        "answer": html.Div([
            html.Ul([
                html.Li("Immediately after forming the trust or society"),
                html.Li("Before filing the first Income Tax Return (ITR) to claim exemption"),
            ])
        ])
    },
    {
        "id": "Q33",
        "question": "Why is 12AA registration important for a school?",
        "answer": html.Div([
            html.Ul([
                html.Li("Enables the school to claim exemption for income used for educational/charitable purposes"),
                html.Li("Without 12AA, the income is taxable even if spent on charitable activities"),
            ])
        ])
    },
    {
        "id": "Q34",
        "question": "What documents are required to apply for 12AA registration?",
        "answer": html.Div([
            html.Ul([
                html.Li("Trust Deed (for a trust) or MOA & Rules (for a society)"),
                html.Li("PAN card of the trust/society"),
                html.Li("Proof of address (electricity bill, property papers)"),
                html.Li("Financial statements or audited accounts (if available)"),
                html.Li("Details of activities and objectives of the school"),
                html.Li("List of trustees or managing committee members"),
                html.Li("Bank account details"),
                html.Li("Covering letter requesting registration"),
            ])
        ])
    },

    # ---------- Section B: 80G Registration (Donor Deduction for Donations) ----------
    {
        "id": "Q35",
        "question": "What is 80G registration for a school?",
        "answer": html.Div(
            "80G registration allows a school to issue donation receipts to donors, enabling them to claim tax deduction under Section 80G of the Income Tax Act."
        )
    },
    {
        "id": "Q36",
        "question": "When should a school apply for 80G registration?",
        "answer": html.Div([
            html.Ul([
                html.Li("Only after obtaining 12AA registration, because 12AA is a prerequisite"),
                html.Li("Apply when the school wants to receive tax-deductible donations"),
            ])
        ])
    },
    {
        "id": "Q37",
        "question": "Why is 80G registration important?",
        "answer": html.Div([
            html.Ul([
                html.Li("It encourages donors by giving them tax benefits, which helps in raising more donations"),
                html.Li("Without 80G, donors cannot claim deductions for their donations"),
            ])
        ])
    },
    {
        "id": "Q38",
        "question": "What documents are required to apply for 80G registration?",
        "answer": html.Div([
            html.Ul([
                html.Li("12AA registration certificate"),
                html.Li("Trust Deed / MOA & Rules"),
                html.Li("PAN card of the institution"),
                html.Li("Audited accounts or financial statements (preferably last 3 years)"),
                html.Li("Bank account details for donations"),
                html.Li("List of trustees / managing committee members"),
                html.Li("Activity report showing charitable use of funds (e.g., education)"),
                html.Li("Covering letter requesting 80G registration"),
            ])
        ])
    },
    {
        "id": "Q39",
        "question": "Can a school get 80G without 12AA registration?",
        "answer": html.Div(
            "No, 12AA registration is mandatory before applying for 80G."
        )
    },
    {
        "id": "Q40",
        "question": "How long does it take to get 12AA and 80G registration?",
        "answer": html.Div(
            "Typically 2–6 months, depending on the Income Tax Department’s processing time."
        )
    },
    {
        "id": "Q41",
        "question": "Important Compliance Dates for Schools (India)",
        "answer": html.Div([

            # 1. Income Tax – Schools
            html.H6("1. Income Tax – Schools"),

            html.B("TDS Deposit Deadlines"),
            html.Ul([
                html.Li("Monthly: By 7th of the next month"),
                html.Li("March TDS: By 30th April"),
            ]),

            html.B("TDS Return (Quarterly)"),
            html.Ul([
                html.Li("Q1 (April–June): 31 July"),
                html.Li("Q2 (July–September): 31 October"),
                html.Li("Q3 (October–December): 31 January"),
                html.Li("Q4 (January–March): 31 May"),
            ]),

            html.B("TDS Certificates"),
            html.Ul([
                html.Li("Form 16 (Salary): 15 June"),
                html.Li("Form 16A (Non-Salary): Within 15 days of filing TDS return"),
            ]),

            html.B("Income Tax Return (ITR)"),
            html.Ul([
                html.Li("Non-Audit cases: 31 July"),
                html.Li("Audit cases: 31 October"),
            ]),

            html.B("Tax Audit / Charitable Audit"),
            html.Ul([
                html.Li("Audit Report (Form 3CD / Form 10B): 30 September"),
            ]),

            html.B("Advance Tax (If Applicable)"),
            html.Ul([
                html.Li("1st Installment: 15 June"),
                html.Li("2nd Installment: 15 September"),
                html.Li("3rd Installment: 15 December"),
                html.Li("4th Installment: 15 March"),
            ]),

            html.Hr(),

            # 2. Provident Fund
            html.H6("2. Provident Fund (PF – EPFO)"),
            html.Ul([
                html.Li("PF Deposit (Monthly): By 15th of next month"),
                html.Li("PF Return: Monthly Electronic Challan cum Return (ECR) filing"),
            ]),

            html.Hr(),

            # 3. ESI
            html.H6("3. Employee State Insurance (ESI)"),
            html.Ul([
                html.Li("ESI Contribution Deposit (Monthly): By 15th of next month"),
                html.Li("ESI Return (April–September): 11 November"),
                html.Li("ESI Return (October–March): 11 May"),
            ]),

            html.Hr(),

            # 4. Professional Tax
            html.H6("4. Professional Tax (If Applicable – State-wise)"),
            html.Ul([
                html.Li("Professional Tax Payment: Usually 10th–15th (state-specific)"),
                html.Li("Professional Tax Return: Annual / Half-yearly (state-specific)"),
            ]),

            html.Hr(),

            # 5. Labour Law
            html.H6("5. Labour Law / Other Registers"),
            html.Ul([
                html.Li("Labour Registers: Must be maintained throughout the year"),
                html.Li("Annual Returns: Typically 31 January / 31 March (state-specific)"),
            ]),

            html.Hr(),

            # 6. Other Authorities
            html.H6("6. Other Authorities"),
            html.Ul([
                html.Li("FCRA Annual Return (if applicable): 31 December"),
                html.Li("Societies / Trusts Annual Accounts / Return: As per state rules (often 30 September)"),
            ]),

            html.Hr(),

            # 7. Quick Overview
            html.H6("7. Quick Monthly Compliance Overview"),
            html.Ul([
                html.Li("7th: TDS Deposit"),
                html.Li("15th: PF & ESI Deposit"),
                html.Li("15 March: Last installment of Advance Tax"),
                html.Li("31 July: ITR (Non-Audit cases)"),
                html.Li("30 September: Tax Audit / Charitable Audit"),
                html.Li("31 October: ITR (Audit cases)"),
            ]),
        ])
    }
    ],

    "hi": [
        {
            "id": "Q1",
            "question": "स्कूल के लिए टैक्स ऑडिट क्या होता है?",
            "answer": "टैक्स ऑडिट का अर्थ है स्कूल के लेखा-पुस्तकों की जाँच किसी चार्टर्ड अकाउंटेंट द्वारा करना, ताकि आयकर अधिनियम, 1961 के प्रावधानों का पालन सुनिश्चित हो सके।"
        },
        {
            "id": "Q2",
            "question": "क्या सभी स्कूलों के लिए टैक्स ऑडिट अनिवार्य है?",
            "answer": "नहीं। टैक्स ऑडिट केवल उन्हीं स्कूलों के लिए अनिवार्य है जो आय, पंजीकरण और सकल प्राप्तियों से संबंधित निर्धारित शर्तें पूरी करते हैं।"
        },
        {
    "id": "Q3",
    "question": "धारा 44AB के अंतर्गत स्कूल को टैक्स ऑडिट कब कराना होता है?",
    "answer": html.Div([
        html.Div("यदि:"),
        html.Ul([
            html.Li("स्कूल की कर योग्य आय (Taxable Income) है"),
            html.Li("उसकी सकल प्राप्तियाँ ₹1 करोड़ से अधिक हैं"),
        ]),
        html.Div("तो धारा 44AB के अंतर्गत टैक्स ऑडिट अनिवार्य है।")
    ])
}
,
        {
    "id": "Q4",
    "question": "क्या धारा 12AB में पंजीकृत स्कूल को टैक्स ऑडिट कराना होता है?",
    "answer": html.Div([
        html.Ul([
            html.Li("नहीं, यदि स्कूल अपनी 85% या उससे अधिक आय शिक्षा कार्यों में उपयोग करता है और सभी शर्तों का पालन करता है।"),
            html.Li("हाँ, यदि स्कूल शर्तों का उल्लंघन करता है, कर योग्य आय अर्जित करता है या व्यावसायिक गतिविधियाँ करता है।"),
        ])
    ])
}
,
        {
            "id": "Q5",
            "question": "धारा 12AB में पंजीकृत स्कूल के लिए कौन-सा ऑडिट लागू होता है?",
            "answer": "ऐसे स्कूलों को सामान्यतः फॉर्म 10B में चैरिटेबल ऑडिट कराना होता है।"
        },
        {
            "id": "Q6",
            "question": "यदि 12AB पंजीकृत स्कूल की कर योग्य आय हो जाए तो क्या होगा?",
            "answer": "यदि कर योग्य आय उत्पन्न होती है और सकल प्राप्तियाँ निर्धारित सीमा से अधिक हैं, तो धारा 44AB के अंतर्गत टैक्स ऑडिट अनिवार्य हो जाता है।"
        },
        {
            "id": "Q7",
            "question": "जो स्कूल 12AB में पंजीकृत नहीं हैं, क्या उनके लिए टैक्स ऑडिट अनिवार्य है?",
            "answer": "हाँ। यदि ऐसे स्कूल की सकल प्राप्तियाँ ₹1 करोड़ से अधिक हैं, तो टैक्स ऑडिट अनिवार्य है।"
        },
        {
            "id": "Q8",
            "question": "क्या धारा 10(23C) के अंतर्गत छूट प्राप्त स्कूलों को ऑडिट कराना होता है?",
            "answer": "हाँ। धारा 10(23C) के अंतर्गत स्वीकृत स्कूलों को हर वर्ष ऑडिट कराना अनिवार्य है, चाहे उनकी आय कितनी भी हो।"
        },
        {
    "id": "Q9",
    "question": "यदि स्कूल की कोई कर योग्य आय नहीं है, तब भी ऑडिट आवश्यक है?",
    "answer": html.Div([
        html.Ul([
            html.Li("12AB और 10(23C) वाले स्कूलों के लिए, छूट की शर्तों के अनुसार ऑडिट फिर भी अनिवार्य हो सकता है।"),
            html.Li("सामान्य स्कूलों के लिए, यदि कर योग्य आय नहीं है और प्राप्तियाँ निर्धारित सीमा में हैं, तो टैक्स ऑडिट आवश्यक नहीं होता।"),
        ])
    ])
}
,
        {
    "id": "Q10",
    "question": "स्कूलों के लिए कौन-कौन से ऑडिट फॉर्म लागू होते हैं?",
    "answer": html.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("स्कूल का प्रकार"),
                    html.Th("लागू ऑडिट फॉर्म"),
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td("सामान्य कर योग्य स्कूल"),
                    html.Td("फॉर्म 3CA / 3CB व 3CD"),
                ]),
                html.Tr([
                    html.Td("12AB पंजीकृत स्कूल"),
                    html.Td("फॉर्म 10B"),
                ]),
                html.Tr([
                    html.Td("10(23C) स्वीकृत स्कूल"),
                    html.Td("निर्धारित ऑडिट रिपोर्ट"),
                ]),
            ]),
        ],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "fontSize": "13px",
        },
    )
}
,
        {
    "id": "Q11",
    "question": "स्कूल के टैक्स ऑडिट की अंतिम तिथि क्या है?",
    "answer": html.Div([
        html.Ul([
            html.Li("ऑडिट रिपोर्ट की अंतिम तिथि: 30 सितंबर"),
            html.Li("ITR दाखिल करने की अंतिम तिथि: 31 अक्टूबर"),
        ]),
        html.Div(
            "(सरकार द्वारा संशोधन संभव)",
            style={"fontSize": "12px", "color": "#666", "marginTop": "4px"}
        )
    ])
}
,
        {
    "id": "Q12",
    "question": "टैक्स ऑडिट न कराने पर क्या दंड लगता है?",
    "answer": html.Div([
        html.Div("टैक्स ऑडिट न कराने पर:"),
        html.Ul([
            html.Li("धारा 271B के अंतर्गत जुर्माना – टर्नओवर का 0.5% (अधिकतम ₹1.5 लाख)"),
            html.Li("कर छूट रद्द हो सकती है"),
            html.Li("आयकर जांच और कानूनी कार्यवाही हो सकती है"),
        ])
    ])
}
,
        {
            "id": "Q13",
            "question": "क्या विदेशी चंदा मिलने पर टैक्स ऑडिट अनिवार्य हो जाता है?",
            "answer": "कुछ मामलों में विदेशी चंदा प्राप्त होने पर टैक्स ऑडिट अनिवार्य हो सकता है।"
        },
        {
            "id": "Q14",
            "question": "क्या आयकर विभाग स्कूल के लिए विशेष ऑडिट का आदेश दे सकता है?",
            "answer": "हाँ। आयकर विभाग आवश्यक होने पर विशेष ऑडिट का आदेश दे सकता है।"
        },
        {
            "id": "Q15",
            "question": "स्कूल के लिए टैक्स ऑडिट लागू होने का सरल नियम क्या है?",
            "answer": "यदि स्कूल की कर योग्य आय है और सकल प्राप्तियाँ ₹1 करोड़ से अधिक हैं, या 12AB/10(23C) के अंतर्गत ऑडिट अनिवार्य है, तो टैक्स ऑडिट कराना जरूरी है।"
        },
        {
        "id": "Q16",
        "question": "स्कूलों के लिए आयकर अनुपालन क्या है?",
        "answer": html.Div(
            "आयकर अनुपालन का अर्थ है आयकर अधिनियम के अंतर्गत सभी नियमों का पालन करना, जैसे TDS की कटौती व जमा, रिटर्न दाखिल करना, प्रमाणपत्र जारी करना, रिकॉर्ड रखना और आयकर नोटिस का उत्तर देना।"
        )
    },
    {
        "id": "Q17",
        "question": "क्या स्कूल को वेतन पर TDS काटना अनिवार्य है?",
        "answer": html.Div(
            "हाँ। यदि शिक्षकों एवं गैर-शिक्षण कर्मचारियों की आय कर योग्य सीमा से अधिक है, तो धारा 192 के अंतर्गत वेतन पर TDS काटना अनिवार्य है।"
        )
    },
    {
        "id": "Q18",
        "question": "स्कूल को अन्य किन भुगतानों पर TDS काटना होता है?",
        "answer": html.Div([
            html.Div("स्कूल को निम्न भुगतानों पर TDS काटना होता है:"),
            html.Ul([
                html.Li("ठेकेदार को भुगतान (धारा 194C)"),
                html.Li("प्रोफेशनल फीस (धारा 194J)"),
                html.Li("किराया भुगतान (धारा 194I)"),
                html.Li("अन्य लागू सेवाएँ"),
            ])
        ])
    },
    {
        "id": "Q19",
        "question": "यदि TDS समय पर न काटा या जमा न किया जाए तो क्या होगा?",
        "answer": html.Div(
            "ऐसी स्थिति में ब्याज, जुर्माना और लेट फीस लग सकती है तथा आयकर विभाग द्वारा कार्यवाही हो सकती है।"
        )
    },
    {
        "id": "Q20",
        "question": "स्कूल को कौन-कौन से TDS रिटर्न दाखिल करने होते हैं?",
        "answer": html.Div([
            html.Ul([
                html.Li("फॉर्म 24Q – वेतन से संबंधित"),
                html.Li("फॉर्म 26Q – गैर-वेतन भुगतानों से संबंधित"),
            ]),
            html.Div(
                "ये रिटर्न तिमाही आधार पर दाखिल किए जाते हैं।",
                style={"marginTop": "4px"}
            )
        ])
    },
    {
        "id": "Q21",
        "question": "फॉर्म 16 क्या है और कब जारी किया जाता है?",
        "answer": html.Div(
            "फॉर्म 16 वेतन से संबंधित TDS प्रमाणपत्र है, जिसे TDS रिटर्न दाखिल करने के बाद वार्षिक रूप से कर्मचारियों को दिया जाता है।"
        )
    },
    {
        "id": "Q22",
        "question": "फॉर्म 16A क्या है?",
        "answer": html.Div(
            "फॉर्म 16A गैर-वेतन भुगतानों (जैसे ठेकेदार/प्रोफेशनल) के लिए TDS प्रमाणपत्र है, जो तिमाही रूप से जारी किया जाता है।"
        )
    },
    {
        "id": "Q23",
        "question": "क्या स्कूल को आयकर रिटर्न दाखिल करना अनिवार्य है?",
        "answer": html.Div(
            "हाँ। प्रत्येक स्कूल को आयकर रिटर्न (ITR) दाखिल करना अनिवार्य है, चाहे उसकी आय करमुक्त ही क्यों न हो।"
        )
    },
    {
        "id": "Q24",
        "question": "स्कूल आयकर छूट कैसे प्राप्त कर सकता है?",
        "answer": html.Div(
            "स्कूल को धारा 12AB के अंतर्गत पंजीकरण कराना होता है और निर्धारित शर्तों का पालन करना होता है।"
        )
    },
    {
        "id": "Q25",
        "question": "स्कूल को कौन-कौन से रिकॉर्ड रखने होते हैं?",
        "answer": html.Div([
            html.Div("स्कूल को निम्न रिकॉर्ड रखने चाहिए:"),
            html.Ul([
                html.Li("वेतन रजिस्टर"),
                html.Li("भुगतान वाउचर और रसीदें"),
                html.Li("TDS से संबंधित रिकॉर्ड"),
                html.Li("वित्तीय विवरण और ऑडिट रिपोर्ट"),
            ])
        ])
    },
    {
        "id": "Q26",
        "question": "क्या स्कूल के लिए टैक्स ऑडिट अनिवार्य है?",
        "answer": html.Div(
            "यदि आयकर अधिनियम या छूट की शर्तों के अनुसार आवश्यक हो, तो टैक्स ऑडिट अनिवार्य होता है।"
        )
    },
    {
        "id": "Q27",
        "question": "PAN और TAN क्या हैं? क्या ये अनिवार्य हैं?",
        "answer": html.Div([
            html.Ul([
                html.Li("PAN (स्थायी खाता संख्या) – स्कूल की कर पहचान के लिए आवश्यक"),
                html.Li("TAN (कर कटौती खाता संख्या) – TDS से संबंधित कार्यों के लिए अनिवार्य"),
            ])
        ])
    },
    {
        "id": "Q28",
        "question": "यदि स्कूल को आयकर नोटिस प्राप्त हो तो क्या करना चाहिए?",
        "answer": html.Div(
            "स्कूल को निर्धारित समय में उचित उत्तर देना चाहिए और आवश्यक दस्तावेज प्रस्तुत करने चाहिए।"
        )
    },
    {
        "id": "Q29",
        "question": "क्या स्कूल को अग्रिम कर (Advance Tax) देना होता है?",
        "answer": html.Div(
            "यदि स्कूल की आय कर योग्य है, तो अग्रिम कर का भुगतान करना अनिवार्य है।"
        )
    },
    {
        "id": "Q30",
        "question": "आयकर अनुपालन न करने के क्या परिणाम होते हैं?",
        "answer": html.Div([
            html.Div("अनुपालन न करने पर:"),
            html.Ul([
                html.Li("जुर्माना और ब्याज"),
                html.Li("कर छूट रद्द हो सकती है"),
                html.Li("कानूनी कार्यवाही हो सकती है"),
            ])
        ])
    },
    {
        "id": "Q31",
        "question": "स्कूल के लिए 12AA रजिस्ट्रेशन क्या है?",
        "answer": html.Div(
            "12AA रजिस्ट्रेशन आयकर विभाग की स्वीकृति है, जो एक चैरिटेबल ट्रस्ट या सोसाइटी (जैसे स्कूल) को धारा 11 और 12 के तहत आयकर छूट प्राप्त करने की अनुमति देता है।"
        )
    },
    {
        "id": "Q32",
        "question": "स्कूल को 12AA रजिस्ट्रेशन कब कराना चाहिए?",
        "answer": html.Div([
            html.Ul([
                html.Li("स्कूल के ट्रस्ट/सोसाइटी बनने के तुरंत बाद"),
                html.Li("अपनी पहली आयकर रिटर्न (ITR) दाखिल करने से पहले, ताकि छूट का दावा किया जा सके"),
            ])
        ])
    },
    {
        "id": "Q33",
        "question": "12AA रजिस्ट्रेशन क्यों महत्वपूर्ण है?",
        "answer": html.Div([
            html.Ul([
                html.Li("यह स्कूल को शिक्षा या चैरिटेबल उद्देश्य में उपयोग की गई आय पर कर छूट प्राप्त करने में सक्षम बनाता है"),
                html.Li("बिना 12AA के, स्कूल की आय कर योग्य मानी जाएगी"),
            ])
        ])
    },
    {
        "id": "Q34",
        "question": "12AA रजिस्ट्रेशन के लिए आवश्यक दस्तावेज़ कौन-कौन से हैं?",
        "answer": html.Div([
            html.Ul([
                html.Li("ट्रस्ट के लिए ट्रस्ट डीड / सोसाइटी के लिए MOA एवं नियमावली"),
                html.Li("ट्रस्ट/सोसाइटी का PAN कार्ड"),
                html.Li("पते का प्रमाण (बिजली बिल, संपत्ति दस्तावेज़ आदि)"),
                html.Li("वित्तीय विवरण / ऑडिटेड अकाउंट्स (यदि उपलब्ध हों)"),
                html.Li("स्कूल की गतिविधियों और उद्देश्यों का विवरण"),
                html.Li("ट्रस्टी / प्रबंध समिति के सदस्यों की सूची"),
                html.Li("बैंक खाता विवरण"),
                html.Li("रजिस्ट्रेशन हेतु कवरिंग लेटर"),
            ])
        ])
    },

    # ---------- Section B: 80G रजिस्ट्रेशन (दान पर कर लाभ) ----------
    {
        "id": "Q35",
        "question": "स्कूल के लिए 80G रजिस्ट्रेशन क्या है?",
        "answer": html.Div(
            "80G रजिस्ट्रेशन स्कूल को दानदाताओं को कर लाभ वाली रसीदें जारी करने की अनुमति देता है, जिससे दानदाता धारा 80G के तहत टैक्स डिडक्शन का लाभ उठा सकते हैं।"
        )
    },
    {
        "id": "Q36",
        "question": "स्कूल को 80G रजिस्ट्रेशन कब कराना चाहिए?",
        "answer": html.Div([
            html.Ul([
                html.Li("केवल 12AA रजिस्ट्रेशन प्राप्त करने के बाद"),
                html.Li("जब स्कूल टैक्स डिडक्टिबल डोनेशन प्राप्त करना चाहता है"),
            ])
        ])
    },
    {
        "id": "Q37",
        "question": "80G रजिस्ट्रेशन क्यों महत्वपूर्ण है?",
        "answer": html.Div([
            html.Ul([
                html.Li("यह दानदाताओं को कर लाभ देता है, जिससे स्कूल को अधिक दान प्राप्त होता है"),
                html.Li("बिना 80G के, दानदाता दान राशि पर छूट नहीं ले सकते"),
            ])
        ])
    },
    {
        "id": "Q38",
        "question": "80G रजिस्ट्रेशन के लिए आवश्यक दस्तावेज़ कौन-कौन से हैं?",
        "answer": html.Div([
            html.Ul([
                html.Li("12AA रजिस्ट्रेशन प्रमाण पत्र"),
                html.Li("ट्रस्ट डीड / MOA एवं नियमावली"),
                html.Li("संस्था का PAN कार्ड"),
                html.Li("ऑडिटेड अकाउंट्स / वित्तीय विवरण (पिछले 3 वर्ष)"),
                html.Li("दान हेतु बैंक खाता विवरण"),
                html.Li("ट्रस्टी / प्रबंध समिति के सदस्यों की सूची"),
                html.Li("गतिविधियों की रिपोर्ट (दान के उपयोग का विवरण)"),
                html.Li("80G रजिस्ट्रेशन हेतु कवरिंग लेटर"),
            ])
        ])
    },
    {
        "id": "Q39",
        "question": "क्या कोई स्कूल 12AA रजिस्ट्रेशन के बिना 80G ले सकता है?",
        "answer": html.Div(
            "नहीं, 80G के लिए 12AA रजिस्ट्रेशन अनिवार्य है।"
        )
    },
    {
        "id": "Q40",
        "question": "12AA और 80G रजिस्ट्रेशन में कितना समय लगता है?",
        "answer": html.Div(
            "आमतौर पर 2–6 महीने लगते हैं, जो आयकर विभाग की प्रक्रिया पर निर्भर करता है।"
        )
    }
    
    ,
    {
        "id": "Q41",
        "question": "स्कूलों के लिए महत्वपूर्ण अनुपालन तिथियाँ (Income Tax, PF, ESI आदि)",
        "answer": html.Div([

            # 1. Income Tax
            html.H6("1. आयकर (Income Tax) – स्कूलों के लिए"),

            html.B("TDS जमा करने की तिथियाँ"),
            html.Ul([
                html.Li("हर माह: अगले महीने की 7 तारीख तक"),
                html.Li("मार्च माह का TDS: 30 अप्रैल तक"),
            ]),

            html.B("TDS रिटर्न (त्रैमासिक)"),
            html.Ul([
                html.Li("Q1 (अप्रैल–जून): 31 जुलाई"),
                html.Li("Q2 (जुलाई–सितंबर): 31 अक्टूबर"),
                html.Li("Q3 (अक्टूबर–दिसंबर): 31 जनवरी"),
                html.Li("Q4 (जनवरी–मार्च): 31 मई"),
            ]),

            html.B("TDS प्रमाणपत्र"),
            html.Ul([
                html.Li("फॉर्म 16: 15 जून"),
                html.Li("फॉर्म 16A: रिटर्न फाइल करने के 15 दिन के भीतर"),
            ]),

            html.B("आयकर रिटर्न (ITR)"),
            html.Ul([
                html.Li("Non-Audit केस: 31 जुलाई"),
                html.Li("Audit केस: 31 अक्टूबर"),
            ]),

            html.B("टैक्स ऑडिट / चैरिटेबल ऑडिट"),
            html.Ul([
                html.Li("ऑडिट रिपोर्ट (Form 3CD / 10B): 30 सितंबर"),
            ]),

            html.B("एडवांस टैक्स (यदि लागू हो)"),
            html.Ul([
                html.Li("1st किस्त: 15 जून"),
                html.Li("2nd किस्त: 15 सितंबर"),
                html.Li("3rd किस्त: 15 दिसंबर"),
                html.Li("4th किस्त: 15 मार्च"),
            ]),

            html.Hr(),

            # 2. PF
            html.H6("2. भविष्य निधि (PF – EPFO)"),
            html.Ul([
                html.Li("PF जमा: हर माह अगले महीने की 15 तारीख तक"),
                html.Li("PF रिटर्न: मासिक ECR फाइलिंग"),
            ]),

            html.Hr(),

            # 3. ESI
            html.H6("3. कर्मचारी राज्य बीमा (ESI)"),
            html.Ul([
                html.Li("ESI जमा: हर माह अगले महीने की 15 तारीख तक"),
                html.Li("ESI रिटर्न (अप्रैल–सितंबर): 11 नवंबर"),
                html.Li("ESI रिटर्न (अक्टूबर–मार्च): 11 मई"),
            ]),

            html.Hr(),

            # 4. Professional Tax
            html.H6("4. प्रोफेशनल टैक्स (यदि लागू हो)"),
            html.Ul([
                html.Li("भुगतान: राज्य नियमों के अनुसार (आमतौर पर 10–15 तारीख)"),
                html.Li("रिटर्न: वार्षिक / अर्धवार्षिक (राज्य अनुसार)"),
            ]),

            html.Hr(),

            # 5. Labour Law
            html.H6("5. श्रम कानून (Labour Law)"),
            html.Ul([
                html.Li("श्रम रजिस्टर: पूरे वर्ष अद्यतन रखना अनिवार्य"),
                html.Li("वार्षिक रिटर्न: सामान्यतः 31 जनवरी / 31 मार्च"),
            ]),

            html.Hr(),

            # 6. Other Authorities
            html.H6("6. अन्य महत्वपूर्ण प्राधिकरण"),
            html.Ul([
                html.Li("FCRA वार्षिक रिटर्न (यदि लागू हो): 31 दिसंबर"),
                html.Li("सोसाइटी / ट्रस्ट रिटर्न: राज्य नियमों के अनुसार (अक्सर 30 सितंबर)"),
            ]),

            html.Hr(),

            # 7. Quick Overview
            html.H6("7. एक नजर में – मासिक अनुपालन सारांश"),
            html.Ul([
                html.Li("7 तारीख: TDS जमा"),
                html.Li("15 तारीख: PF + ESI जमा"),
                html.Li("15 मार्च: एडवांस टैक्स अंतिम किस्त"),
                html.Li("31 जुलाई: ITR (Non-Audit)"),
                html.Li("30 सितंबर: टैक्स ऑडिट"),
                html.Li("31 अक्टूबर: ITR (Audit)"),
            ]),
        ])
    }

    ]
}

# 🤖 Floating Icon
def get_chatbot_icon():
    return html.Div(
        "🤖",
        id="chatbot-icon",
        n_clicks=0,
        style={
            "position": "fixed",
            "bottom": "calc(40px + 8px)",
            "right": "20px",
            "left": "auto",
            "width": "50px",
            "height": "50px",
            "borderRadius": "50%",
            "backgroundColor": "#E8F5E9",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "cursor": "pointer",
            "fontSize": "26px",
            "boxShadow": "0 4px 10px rgba(0,0,0,0.15)",
            "zIndex": "3000",
        },
    )

def get_similar_questions(user_input, language, threshold=60, top_n=5):
    """
    Returns top-N most similar questions above threshold
    """
    results = []

    for item in QUESTION_BANK[language]:
        score = fuzz.token_set_ratio(user_input, item["question"])

        if score >= threshold:
            results.append({
                "id": item["id"],
                "question": item["question"],
                "score": score
            })

    # Sort by highest similarity
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_n]
# 🪟 Chatbot Popup
def get_chatbot_popup():
    return html.Div(
        [
            dcc.Store(id="chatbot-lang-state", data="en"),

            html.Div(
                [

                    # ❌ Close button
                    html.Div(
                        "✕",
                        id="chatbot-close",
                        n_clicks=0,
                        style={
                            "position": "absolute",
                            "top": "10px",
                            "right": "12px",
                            "cursor": "pointer",
                            "color": "#777",
                            "fontSize": "14px",
                        },
                    ),

                    # 🔝 Header
                    html.Div(
                        "Assistant Bot",
                        style={
                            "fontWeight": "600",
                            "fontSize": "14px",
                            "textAlign": "center",
                            "paddingBottom": "6px",
                            "borderBottom": "1px solid #eee",
                        },
                    ),

                    # 🌐 Language switch
                    html.Div(
                        [
                            html.Button(
                                "English",
                                id="lang-en",
                                n_clicks=0,
                                style={
                                    "padding": "6px 16px",
                                    "borderRadius": "18px",
                                    "border": "1px solid #4CAF50",
                                    "backgroundColor": "#E8F5E9",
                                    "fontSize": "12px",
                                },
                            ),
                            html.Button(
                                "हिंदी",
                                id="lang-hi",
                                n_clicks=0,
                                style={
                                    "padding": "6px 16px",
                                    "borderRadius": "18px",
                                    "border": "1px solid #ddd",
                                    "backgroundColor": "#fff",
                                    "fontSize": "12px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "center",
                            "gap": "10px",
                            "padding": "8px 0",
                            "borderBottom": "1px solid #eee",
                            "marginBottom": "6px",
                        },
                    ),

                    # 💬 Chat body
                    html.Div(
                        [
                            # Messages
                            html.Div(
                           
                                id="chatbot-messages",
                                style={
                                    "flex": "1",
                                    
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "8px",
                                    "padding": "4px",
                                },
                            ),
                            html.Div(
    html.Button(
        "📚 Show All Questions",
        id="show-all-questions",
        n_clicks=0,
        style={
            "border": "1px solid #4CAF50",
            "backgroundColor": "#E8F5E9",
            "borderRadius": "16px",
            "padding": "6px 12px",
            "fontSize": "12px",
            "cursor": "pointer",
        },
    ),
    style={"textAlign": "center", "marginBottom": "6px"}
),

                            # Input + Send
                            html.Div(
                                [
                                    dcc.Input(
                                        id="chatbot-input",
                                        placeholder="Type your message…",
                                        type="text",
                                        debounce=True,
                                        style={
                                            "flex": "1",
                                            "border": "1px solid #ddd",
                                            "borderRadius": "20px",
                                            "padding": "10px 14px",
                                            "fontSize": "13px",
                                            "outline": "none",
                                        },
                                    ),
                                    html.Button(
                                        "➤",
                                        id="chatbot-send",
                                        n_clicks=0,
                                        style={
                                            "marginLeft": "6px",
                                            "borderRadius": "50%",
                                            "border": "none",
                                            "backgroundColor": "#4CAF50",
                                            "color": "#fff",
                                            "width": "36px",
                                            "height": "36px",
                                            "cursor": "pointer",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "padding": "6px",
                                    "position": "sticky",
                                    "bottom": "0",
                                    "backgroundColor": "#fff",
                                },
                            ),
                        ],
                        id="chatbot-scroll-container",
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "height": "55vh",
                            "overflow": "auto",
                        },
                    ),
                ],
                style={
                    "position": "relative",
                    "width": "min(92vw, 360px)",
                    "backgroundColor": "#fff",
                    "borderRadius": "18px",
                    "boxShadow": "0 12px 40px rgba(0,0,0,0.25)",
                    "padding": "14px",
                    "fontFamily": "Segoe UI, Arial",
                },
            )
        ],
        id="chatbot-popup",
        style={
            "position": "fixed",
            "bottom": "110px",
            "right": "20px",
            "display": "none",
            "zIndex": "3000",
        },
    )


WELCOME_MESSAGE = html.Div(
    "Hello! 👋 How can I help you?",
    style={
        "alignSelf": "flex-start",
        "backgroundColor": "#FFFDE7",
        "padding": "10px 12px",
        "borderRadius": "12px",
        "fontSize": "13px",
        "maxWidth": "85%",
        "borderTopLeftRadius": "4px",
    },
)

def get_clean_input(raw_text):
    if not raw_text:
        return ""
    return raw_text.strip().lower()


@callback(
    Output("chatbot-messages", "children", allow_duplicate=True),
    Output("chatbot-input", "value"),          # 👈 REQUIRED
    Input("chatbot-send", "n_clicks"),
    State("chatbot-input", "value"),
    State("chatbot-lang-state", "data"),
    State("chatbot-messages", "children"),
    prevent_initial_call=True,
)

def chat_flow(send_clicks, raw_text, lang, messages):

    if messages is None:
        messages = []

    if not raw_text or not raw_text.strip():
        raise dash.exceptions.PreventUpdate

    # 🔹 ORIGINAL (UI)
    display_text = raw_text.strip()

    # 🔹 CLEAN (logic)
    clean_text = get_clean_input(raw_text)

    # 🧹 REMOVE OLD SUGGESTIONS
    messages = remove_old_suggestions(messages)

    # ✅ welcome once
    if not messages:
        messages.append(
            WELCOME_MESSAGE if lang == "en"
            else html.Div("नमस्ते! 👋 मैं आपकी कैसे मदद कर सकता हूँ?",
                          style=WELCOME_MESSAGE.style)
        )

    # 👤 USER MESSAGE
    messages.append(
        html.Div(
            display_text,
            style={
                "alignSelf": "flex-end",
                "backgroundColor": "#E3F2FD",
                "padding": "8px 12px",
                "borderRadius": "12px",
                "borderTopRightRadius": "4px",
                "fontSize": "13px",
                "maxWidth": "85%",
            },
        )
    )

    # 🤖 MATCHING
    matches = get_similar_questions(clean_text, lang)

    if matches:
        for match in matches:
            messages.append(
                html.Div(
                    match["question"],
                    id={"type": "suggested-question", "index": match["id"]},
                    n_clicks=0,
                    style={
                        "alignSelf": "flex-start",
                        "backgroundColor": "#E8F5E9",
                        "padding": "8px 12px",
                        "borderRadius": "12px",
                        "borderTopLeftRadius": "4px",
                        "fontSize": "13px",
                        "cursor": "pointer",
                        "maxWidth": "85%",
                        "border": "1px dashed #C8E6C9",
                    },
                )
            )

    return messages, ""


@callback(
    Output("chatbot-popup", "style" ),
    Output("chatbot-messages", "children"),
    Input("chatbot-icon", "n_clicks"),
    Input("chatbot-close", "n_clicks"),
    State("chatbot-popup", "style"),
    State("chatbot-lang-state", "data"),
    prevent_initial_call=True,
)
def toggle_chatbot(open_clicks, close_clicks, style, lang):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    # ❌ Close
    if trigger == "chatbot-close":
        style["display"] = "none"
        return style, dash.no_update

    # 🤖 Open chatbot
    style["display"] = "block" if style["display"] == "none" else "none"

    # ✅ Inject welcome message on OPEN
    if style["display"] == "block":
        welcome = (
            [WELCOME_MESSAGE]
            if lang == "en"
            else [
                html.Div(
                    "नमस्ते! 👋 मैं आपकी कैसे मदद कर सकता हूँ?",
                    style=WELCOME_MESSAGE.style,
                )
            ]
        )
        return style, welcome

    return style, dash.no_update


@callback(
    Output("chatbot-messages", "children", allow_duplicate=True),
    Input({"type": "suggested-question", "index": ALL}, "n_clicks"),
    State("chatbot-lang-state", "data"),
    State("chatbot-messages", "children"),
    prevent_initial_call=True,
)
def show_answer(n_clicks, lang, messages):

    if not any(n_clicks):
        raise dash.exceptions.PreventUpdate

    if messages is None:
        messages = []

    # 🧹 remove old suggestions
    messages = remove_old_suggestions(messages)

    ctx = dash.callback_context
    triggered_id = ctx.triggered_id["index"]

    for item in QUESTION_BANK[lang]:
        if item["id"] == triggered_id:

            # 👤 show question as user message
            messages.append(
                html.Div(
                    item["question"],
                    style={
                        "alignSelf": "flex-end",
                        "backgroundColor": "#E3F2FD",
                        "padding": "8px 12px",
                        "borderRadius": "12px",
                        "borderTopRightRadius": "4px",
                        "fontSize": "13px",
                        "maxWidth": "85%",
                    },
                )
            )

            # 🤖 bot answer
            messages.append(
                html.Div(
                    item["answer"]
                    if isinstance(item["answer"], list)
                    else [item["answer"]],
                    style={
                        "alignSelf": "flex-start",
                        "backgroundColor": "#FFFDE7",
                        "padding": "10px 12px",
                        "borderRadius": "12px",
                        "fontSize": "13px",
                        "maxWidth": "85%",
                    },
                )
            )
            break

    return messages

@callback(
    Output("chatbot-lang-state", "data"),
    Output("chatbot-messages", "children", allow_duplicate=True),
    Output("lang-en", "style"),
    Output("lang-hi", "style"),
    Input("lang-en", "n_clicks"),
    Input("lang-hi", "n_clicks"),
    prevent_initial_call=True,
)
def switch_language(en, hi):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    if ctx.triggered_id == "lang-hi":
        return (
            "hi",
            [
                html.Div(
                    "नमस्ते! 👋 मैं आपकी कैसे मदद कर सकता हूँ?",
                    style=WELCOME_MESSAGE.style,
                )
            ],
            # English inactive
            {
                "padding": "6px 16px",
                "borderRadius": "18px",
                "border": "1px solid #ddd",
                "backgroundColor": "#fff",
                "fontSize": "12px",
            },
            # Hindi active
            {
                "padding": "6px 16px",
                "borderRadius": "18px",
                "border": "1px solid #4CAF50",
                "backgroundColor": "#E8F5E9",
                "fontSize": "12px",
            },
        )

    # English clicked
    return (
        "en",
        [WELCOME_MESSAGE],
        # English active
        {
            "padding": "6px 16px",
            "borderRadius": "18px",
            "border": "1px solid #4CAF50",
            "backgroundColor": "#E8F5E9",
            "fontSize": "12px",
        },
        # Hindi inactive
        {
            "padding": "6px 16px",
            "borderRadius": "18px",
            "border": "1px solid #ddd",
            "backgroundColor": "#fff",
            "fontSize": "12px",
        },
    )

def remove_old_suggestions(messages):
    if not messages:
        return messages

    cleaned = []

    for m in messages:
        # Dash component comes as dict
        if isinstance(m, dict):
            props = m.get("props", {})
            comp_id = props.get("id")

            # ❌ remove only suggestion cards
            if isinstance(comp_id, dict) and comp_id.get("type") == "suggested-question":
                continue

            cleaned.append(m)
        else:
            cleaned.append(m)

    return cleaned


@callback(
    Output("chatbot-messages", "children", allow_duplicate=True),
    Input("show-all-questions", "n_clicks"),
    State("chatbot-lang-state", "data"),
    State("chatbot-messages", "children"),
    prevent_initial_call=True,
)
def show_all_questions(n_clicks, lang, messages):

    if messages is None:
        messages = []

    messages = remove_old_suggestions(messages)

    # Language based heading
    heading = (
        "Here are all available questions:"
        if lang == "en"
        else "यहाँ सभी उपलब्ध प्रश्न हैं:"
    )

    messages.append(
        html.Div(
            heading,
            style={
                "alignSelf": "flex-start",
                "backgroundColor": "#FFFDE7",
                "padding": "8px 12px",
                "borderRadius": "12px",
                "fontSize": "13px",
                "maxWidth": "85%",
            },
        )
    )

    # Show questions according to language
    for item in QUESTION_BANK.get(lang, []):

        messages.append(
            html.Div(
                item["question"],
                id={"type": "suggested-question", "index": item["id"]},
                n_clicks=0,
                style={
                    "alignSelf": "flex-start",
                    "backgroundColor": "#E8F5E9",
                    "padding": "8px 12px",
                    "borderRadius": "12px",
                    "borderTopLeftRadius": "4px",
                    "fontSize": "13px",
                    "cursor": "pointer",
                    "maxWidth": "85%",
                    "border": "1px dashed #C8E6C9",
                },
            )
        )

    return messages





@callback(
    Output("show-all-questions", "children"),
    Input("chatbot-lang-state", "data")
)
def update_show_all_label(lang):

    if lang == "hi":
        return "📚 सभी प्रश्न देखें"

    return "📚 Show All Questions"