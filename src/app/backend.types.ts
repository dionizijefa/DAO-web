export class SmilesInput {
    smilesInput: string;
}

export class Prediction {
    predictedProbability: number;
    approvedP: number;
    withdrawnP: number;
    predictedClass: number;
    moleculeVis: string;
}

export class Explanation {
    graph: string;
    featureImportance: string;
}

export class Complementary {
    prediction: number;
    tasks: string;
    force; string
}
