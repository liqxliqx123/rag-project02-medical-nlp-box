export const getDomainFromUrl = () => {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('domain') || 'medical';
};

export const getDomainConfig = (domain) => {
  if (domain === 'financial') {
    return {
      title: '金融实体识别',
      icon: '💰',
      placeholder: '请输入需要进行实体识别的金融文本...',
      termTypes: {
        currency: false,
        ratio: false,
        instrument: false,
        institution: false,
        indicator: false,
        accounting: false,
        allFinancialTerms: false,
      },
      termTypeLabels: {
        currency: '货币',
        ratio: '财务比率',
        instrument: '金融工具',
        institution: '金融机构',
        indicator: '金融指标',
        accounting: '会计术语',
        allFinancialTerms: '所有金融术语',
      },
      colorMap: {
        'CURRENCY': '#4CAF50',
        'FINANCIAL_RATIO': '#2196F3',
        'FINANCIAL_INSTRUMENT': '#FF9800',
        'FINANCIAL_INSTITUTION': '#9C27B0',
        'FINANCIAL_INDICATOR': '#F44336',
        'ACCOUNTING_TERM': '#607D8B',
        'ORG': '#3F51B5',
        'MISC': '#795548',
        'PER': '#E91E63',
      },
      embeddingOptions: {
        provider: 'huggingface',
        model: 'BAAI/bge-m3',
        dbName: 'financial_bge_m3',
        collectionName: 'financial_concepts',
      }
    };
  } else {
    return {
      title: '医疗实体识别',
      icon: '🏥',
      placeholder: '请输入需要进行命名实体识别的医疗文本...',
      termTypes: {
        symptom: false,
        disease: false,
        therapeuticProcedure: false,
        allMedicalTerms: false,
      },
      termTypeLabels: {
        symptom: '症状',
        disease: '疾病',
        therapeuticProcedure: '治疗程序',
        allMedicalTerms: '所有医疗术语',
      },
      colorMap: {
        'DATE': "#FF9800",
        'AGE': "#E91E63",
        'SIGN_SYMPTOM': "#FF0000",
        'TIME': "#673AB7",
        'HEIGHT': "#3F51B5",
        'CLINICAL_EVENT': "#2196F3",
        'SHAPE': "#03A9F4",
        'FREQUENCY': "#00BCD4",
        'BIOLOGICAL_STRUCTURE': "#009688",
        'AREA': "#4CAF50",
        'WEIGHT': "#8BC34A",
        'TEXTURE': "#CDDC39",
        'COREFERENCE': "#FFEB3B",
        'MEDICATION': "#FFC107",
        'MASS': "#FF9800",
        'SEVERITY': "#FF5722",
        'BIOLOGICAL_ATTRIBUTE': "#795548",
        'DISEASE_DISORDER': "#00FF00",
        'DURATION': "#607D8B",
        'VOLUME': "#D32F2F",
        'THERAPEUTIC_PROCEDURE': "#C2185B",
        'ADMINISTRATION': "#7B1FA2",
        'ACTIVITY': "#512DA8",
        'SUBJECT': "#303F9F",
        'FAMILY_HISTORY': "#1976D2",
        'HISTORY': "#0288D1",
        'QUANTITATIVE_CONCEPT': "#0097A7",
        'LAB_VALUE': "#00796B",
        'DETAILED_DESCRIPTION': "#388E3C",
        'DIAGNOSTIC_PROCEDURE': "#689F38",
        'NONBIOLOGICAL_LOCATION': "#AFB42B",
        'OUTCOME': "#FBC02D",
        'SEX': "#FFA000",
        'COLOR': "#F57C00",
        'QUALITATIVE_CONCEPT': "#E64A19",
        'DISTANCE': "#5D4037",
        'PERSONAL_BACKGROUND': "#616161",
        'OTHER_ENTITY': "#455A64",
        'OTHER_EVENT': "#C62828",
        'DOSAGE': "#AD1457",
        'OCCUPATION': "#880E4F",
        'COMBINED_BIO_SYMPTOM': "#FF4500",
      },
      embeddingOptions: {
        provider: 'huggingface',
        model: 'BAAI/bge-m3',
        dbName: 'snomed_bge_m3',
        collectionName: 'concepts_only_name',
      }
    };
  }
}; 