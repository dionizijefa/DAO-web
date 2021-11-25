import pickle
import matplotlib
from standardiser import standardise
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from io import StringIO
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import RDConfig, DataStructs
from rdkit.Chem import HybridizationType, ChemicalFeatures, rdDepictor, MolFromSmiles
from rdkit.Chem.AllChem import GetMorganFingerprintAsBitVect
from rdkit.Chem.Draw import rdMolDraw2D
from scipy.stats import zscore
from torch_geometric.data import Data
from torch_geometric.nn import EGConv, global_mean_pool, GNNExplainer
from torch.nn import Sequential, BatchNorm1d, ReLU, Linear, Module, ModuleList
from torch import load, Tensor, long, zeros, manual_seed
import seaborn as sns
from random import seed
import shap
from rdkit.Chem import QED

fdef_name = Path(RDConfig.RDDataDir) / 'BaseFeatures.fdef'
factory = ChemicalFeatures.BuildFeatureFactory(str(fdef_name))

regression_tasks = ['Caco2_Wang', 'Lipophilicity_AstraZeneca','Solubility_AqSolDB', 'PPBR_AZ', 'VDss_Lombardo',
                     'Half_Life_Obach', 'Clearance_Hepatocyte_AZ', 'LD50_Zhu']
classification_tasks = ['HIA_Hou','Pgp_Broccatelli', 'Bioavailability_Ma', 'BBB_Martins', 'CYP2C19_Veith',
                    'CYP2D6_Veith', 'CYP3A4_Veith', 'CYP1A2_Veith', 'CYP2C9_Veith','CYP2C9_Substrate_CarbonMangels',
                     'CYP2D6_Substrate_CarbonMangels','CYP3A4_Substrate_CarbonMangels', 'hERG', 'AMES', 'DILI',
                    'Skin Reaction', 'Carcinogens_Languin','ClinTox','nr-ar', 'nr-ar-lbd', 'nr-ahr', 'nr-aromatase',
                     'nr-er','nr-er-lbd', 'nr-ppar-gamma', 'sr-are', 'sr-atad5', 'sr-hse', 'sr-mmp','sr-p53']

root = root = Path(__file__).resolve().parents[0].absolute()

def one_hot_vector(val, lst):
    """Converts a value to a one-hot vector based on options in lst"""
    if val not in lst:
        val = lst[-1]
    return map(lambda x: x == val, lst)


class EGConvNet(Module):
    """Multi aggregators = ['sum', 'mean', 'max'] or
    ['symnorm']"""
    def __init__(self, hidden_channels, num_layers, num_heads, num_bases, aggregator):
        super().__init__()

        self.lin1 = Linear(27, hidden_channels)
        self.norm1 = BatchNorm1d(hidden_channels)

        self.convs = ModuleList()
        self.norms = ModuleList()
        for _ in range(num_layers):
            self.convs.append(
                EGConv(hidden_channels, hidden_channels, aggregator,
                       num_heads, num_bases))
            self.norms.append(BatchNorm1d(hidden_channels))

        self.mlp = Sequential(
            Linear(hidden_channels, hidden_channels // 2, bias=False),
            BatchNorm1d(hidden_channels // 2),
            ReLU(inplace=True),
            Linear(hidden_channels // 2, hidden_channels // 4, bias=False),
            BatchNorm1d(hidden_channels // 4),
            ReLU(inplace=True),
            Linear(hidden_channels // 4, 1),
        )

    def forward(self, x, edge_index, batch):
        #x = torch.tensor(x).to(torch.int64) za GNN explainer
        x = self.lin1(x)
        x = self.norm1(x)
        x = x.relu_()

        for conv, norm in zip(self.convs, self.norms):
            h = conv(x, edge_index)
            h = norm(h)
            h = h.relu_()
            x = x + h

        x = global_mean_pool(x, batch)

        return self.mlp(x)


class DAOWeb:
    def __init__(self):
        print(root)
        state_dict = load(root / 'state_dict.pt')
        hyperparams = state_dict['hyper_parameters']
        self.model = EGConvNet(
            hyperparams['hidden_channels'],
            hyperparams['num_layers'],
            hyperparams['num_heads'],
            hyperparams['num_bases'],
            aggregator=['sum', 'mean', 'max'])
        self.model.load_state_dict(state_dict['state_dict'])
        self.model.eval()

    def smiles2graph(self, data, **kwargs):
        """
        Converts SMILES string to graph Data object
        :input: SMILES string (str)
        :return: graph object
        """

        mol = MolFromSmiles(r'{}'.format(data))

        """
        if 'descriptors' in kwargs:
            descriptors = kwargs['descriptors']
            descriptors = descriptors[ozren_selected].values[0]
        """

        # atoms
        donor = []
        acceptor = []
        features = []
        names = []
        donor_string = []

        for atom in mol.GetAtoms():
            atom_feature_names = []
            atom_features = []
            atom_features += one_hot_vector(
                atom.GetAtomicNum(),
                [5, 6, 7, 8, 9, 15, 16, 17, 35, 53, 999]
            )

            atom_feature_names.append(atom.GetSymbol())
            atom_features += one_hot_vector(
                atom.GetTotalNumHs(),
                [0, 1, 2, 3, 4]
            )
            atom_feature_names.append(atom.GetTotalNumHs())
            atom_features += one_hot_vector(
                atom.GetHybridization(),
                [HybridizationType.S, HybridizationType.SP, HybridizationType.SP2, HybridizationType.SP3,
                 HybridizationType.SP3D, HybridizationType.SP3D2, HybridizationType.UNSPECIFIED]
            )
            atom_feature_names.append(atom.GetHybridization().__str__())

            atom_features.append(atom.IsInRing())
            atom_features.append(atom.GetIsAromatic())

            if atom.GetIsAromatic() == 1:
                atom_feature_names.append('Aromatic')
            else:
                atom_feature_names.append('Non-aromatic')

            if atom.IsInRing() == 1:
                atom_feature_names.append('Is in ring')
            else:
                atom_feature_names.append('Not in ring')

            donor.append(0)
            acceptor.append(0)

            donor_string.append('Not a donor or acceptor')

            atom_features = np.array(atom_features, dtype=int)
            atom_feature_names = np.array(atom_feature_names, dtype=object)
            features.append(atom_features)
            names.append(atom_feature_names)

        feats = factory.GetFeaturesForMol(mol)
        for j in range(0, len(feats)):
            if feats[j].GetFamily() == 'Donor':
                node_list = feats[j].GetAtomIds()
                for k in node_list:
                    donor[k] = 0
                    donor_string[k] = 'Donor'
            elif feats[j].GetFamily() == 'Acceptor':
                node_list = feats[j].GetAtomIds()
                for k in node_list:
                    acceptor[k] = 1
                    donor_string[k] = 'Acceptor'

        features = np.array(features, dtype=int)
        donor = np.array(donor, dtype=int)
        donor = donor[..., np.newaxis]
        acceptor = np.array(acceptor, dtype=int).transpose()
        acceptor = acceptor[..., np.newaxis]
        x = np.append(features, donor, axis=1)
        x = np.append(x, acceptor, axis=1)

        donor_string = np.array(donor_string, dtype=object)
        donor_string = donor_string[..., np.newaxis]

        names = np.array(names, dtype=object)
        names = np.append(names, donor_string, axis=1)

        # bonds
        num_bond_features = 3  # bond type, bond stereo, is_conjugated
        if len(mol.GetBonds()) > 0:  # mol has bonds
            edges_list = []
            for bond in mol.GetBonds():
                i = bond.GetBeginAtomIdx()
                j = bond.GetEndAtomIdx()

                # add edges in both directions
                edges_list.append((i, j))
                edges_list.append((j, i))

            # data.edge_index: Graph connectivity in COO format with shape [2, num_edges]
            edge_index = np.array(edges_list, dtype=np.int64).T

        else:  # mol has no bonds
            edge_index = np.empty((2, 0), dtype=np.int64)

        graph = dict()
        graph['edge_index'] = Tensor(edge_index).long()
        graph['node_feat'] = Tensor(x)
        graph['feature_names'] = names

        """
        if 'descriptors' in kwargs:
            graph['descriptors'] = Tensor([descriptors.astype(float)])
            return Data(x=graph['node_feat'], edge_index=graph['edge_index'], feature_names=names,
                        descriptors=graph['descriptors'])
        else:
            return Data(x=graph['node_feat'], edge_index=graph['edge_index'], feature_names=names)
        """
        return Data(x=graph['node_feat'], edge_index=graph['edge_index'], feature_names=names)

    def predict(self, smiles):

        smiles = standardise.run(r'{}'.format(smiles))
        mol = MolFromSmiles(r'{}'.format(smiles))
        rdDepictor.Compute2DCoords(mol)
        drawer = rdMolDraw2D.MolDraw2DSVG(400, 200)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText().replace('svg:', '')

        data = self.smiles2graph(r'{}'.format(smiles))
        data.batch = zeros(data.num_nodes, dtype=long)
        output = self.model(data.x, data.edge_index, data.batch).detach().cpu().numpy()[0][0]
        output = round(((1 / (1 + np.exp(-output))) * 100), 2)
        predicted_class = 1 if output > 53 else 0
        approved_calibration = np.loadtxt(root / 'approved_calibration.csv') * 100
        withdrawn_calibration = np.loadtxt(root / 'withdrawn_calibration.csv') * 100
        approved_p_value = (np.searchsorted(approved_calibration, (100-output))) \
                           / (len(approved_calibration) + 1)
        withdrawn_p_value = (np.searchsorted(withdrawn_calibration, output)) \
                            / (len(withdrawn_calibration) + 1)

        qed_prop = QED.properties(mol)
        qed = QED.default(mol)

        qed_prop = {
            'MW': round(qed_prop[0], 2),
            'ALOGP': round(qed_prop[1], 2),
            'HBA': qed_prop[2],
            'HBD': qed_prop[3],
            'PSA': round(qed_prop[4], 2),
            'ROTB': qed_prop[5],
            'AROM': qed_prop[6],
            'ALERTS': qed_prop[7],
            'QED': round(qed*100, 2),
        }
        
        data = pd.read_csv('./master_web.csv', index_col=0)
        mols = [MolFromSmiles(i) for i in data['standardized_smiles']]
        fps = [GetMorganFingerprintAsBitVect(mol, 2, 1024) for mol in mols]
        query = GetMorganFingerprintAsBitVect(mol, 2, 1024)
        sims = np.array(DataStructs.BulkTanimotoSimilarity(query, fps))
        data['query_similarity'] = sims
        wd_sim = data.loc[data['wd_consensus_1'] == 1].sort_values(by='query_similarity', ascending=False)[:3]
        ad_sim = data.loc[data['wd_consensus_1'] == 0].sort_values(by='query_similarity', ascending=False)[:3]
        wd_sim['status'] = 'Withdrawn'
        ad_sim['status'] = 'Approved'
        sims = pd.concat([wd_sim, ad_sim]).sort_values('query_similarity', ascending=False)

        sim_dict = {
            'chembl_id':
                list(sims['chembl_id']),
            'atc_code':
                list(sims['atc_code']),
            'tanimoto_similarity':
                list(sims['query_similarity'].round(2)),
            'name':
                list(sims['name']),
            'status':
                list(sims['status']),
        }

        # calculate similarity to second level ATC codes
        data['atc_code'] = data['atc_code'].str.split(',')
        data = data.explode('atc_code')
        data = data.loc[data['atc_code'] != 'None']
        data['atc_code'] = data['atc_code'].str.rstrip(' ').str.lstrip(' ')
        data['atc_code'] = data['atc_code'].str[:3]
        hue = []
        fingerprints = []
        for i in data['atc_code'].unique():
            disease = data.loc[data['atc_code'] == i]['standardized_smiles']
            interim_fps = []
            for j in disease:
                mol = MolFromSmiles(j)
                fp = GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
                interim_fps.append(fp)
            fingerprints.append(interim_fps)
            hue.append(i)
        disease_dict = dict(zip(hue, fingerprints))
        results = dict()
        for i in disease_dict:
            similarity = []
            for mol in disease_dict[i]:
                similarity.append(DataStructs.FingerprintSimilarity(mol, query))
            results[i] = np.mean(similarity)
        results = pd.DataFrame(results, index=[0]).transpose().sort_values(0, ascending=False).reset_index()[:3]
        sim_atc = {
            '0': [results.iloc[0]['index'], round(results.iloc[0][0], 2)], #0 is the column name
            '1': [results.iloc[1]['index'], round(results.iloc[1][0], 2)],
            '2': [results.iloc[2]['index'], round(results.iloc[2][0], 2)],
        }
        similarities = {'similarity': sim_dict, 'atc_similarity': sim_atc}
        
        return output, predicted_class, round(approved_p_value, 2), round(withdrawn_p_value, 2), svg, qed_prop, similarities

    def explain(self, smiles, epochs=75):
        features = ["boron", "carbon", "nitrogen", "oxygen", "fluorine", "phosphorus", "sulfur",
                    "chlorine", "bromine", "iodine", "other", "zero_Hs", "one_H", "two_Hs", "three_Hs",
                    "four_Hs", "s", "sp", "sp2", "sp3", "sp3d", "sp3d2", "unspecified_hybr",
                    "in_ring", "aromatic", "donor", "acceptor"]

        # set seeds for initializing mask in GNN explainer
        manual_seed(0)
        seed(0)
        np.random.seed(0)

        explainer = GNNExplainer(self.model, epochs=epochs)
        smiles = standardise.run(r'{}'.format(smiles))
        data = self.smiles2graph(smiles)
        data.batch = zeros(data.num_nodes, dtype=long)
        node_feat_mask, edge_mask = explainer.explain_graph(data.x, data.edge_index)

        # node importance
        node_feat_mask = node_feat_mask.detach().numpy()
        node_feat_importance = pd.DataFrame(data=node_feat_mask[np.newaxis], columns=features, index=[0])


        # edge importance
        edge_mask = edge_mask.detach().numpy()
        edge_mask = abs(zscore(edge_mask))
        highlighted_edges = list((np.where(edge_mask >= 1)[0]).astype(object))
        edge_index = data.edge_index.detach().cpu().numpy()

        # edge indices contain both direction so we need to drop one and save a copy
        final_edge = edge_index[:, ::2]
        normal = []  # first direction in edge mask
        reverse = []  # second direction
        for high in highlighted_edges:
            normal.append(list(edge_index[:, high]))
            reverse.append(list(edge_index[:, high][::-1]))

        # find bonds to higlight
        bonds_to_highlight = []
        for i in range(len(final_edge[0])):
            atom_1 = final_edge[0][i]
            atom_2 = final_edge[1][i]
            bond = [atom_1, atom_2]
            if bond in normal:
                bonds_to_highlight.append(i)
                continue
            if bond in reverse:
                bonds_to_highlight.append(i)

        mol = MolFromSmiles(r'{}'.format(smiles))
        rdDepictor.Compute2DCoords(mol)
        drawer = rdMolDraw2D.MolDraw2DSVG(400, 200)
        drawer.DrawMolecule(mol, highlightAtoms=[], highlightBonds=bonds_to_highlight)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText().replace('svg:', '')
        molecule_vis = svg

        # plt.rcParams['svg.fonttype'] = 'none'
        px = 1 / plt.rcParams['figure.dpi']
        fig, ax = plt.subplots(figsize=(200*px, 400*px))
        #fig.tight_layout()
        ax.set_xlim(0, 1)
        ax.yaxis.label.set_size(60)
        ax.xaxis.label.set_color('#66615b')
        ax.tick_params(axis='x', colors='#66615b')
        ax.tick_params(axis='y', colors='#66615b')
        sns.barplot(data=node_feat_importance, orient='horizontal', ax=ax)
        img = StringIO()
        fig.savefig(img, format='svg', bbox_inches="tight")
        img = img.getvalue()
        plt.close()

        """Atom symbols in feature importance
        mol = Chem.MolFromSmiles(r'{}'.format(smiles))
        atoms = []
        for i in bonds_to_highlight:
            atoms.append(mol.GetBonds()[i].GetBeginAtomIdx())
            atoms.append(mol.GetBonds()[i].GetEndAtomIdx())
        symbols = []
        for i in atoms:
            symbols.append(mol.GetAtoms()[i].GetSymbol())
        """

        return molecule_vis, img

    def complementary_model(self, smiles, withdrawn_prob):
        compl_root = Path(__file__).resolve().parents[1].absolute()

        predictions = []
        predictions.append(round(withdrawn_prob/100, 2))
        tasks = ['predict_withdrawn',
                 'CYP2C9_Substrate_CarbonMangels',
                 'nr-ppar-gamma',
                 'Bioavailability_Ma',
                 'Clearance_Hepatocyte_AZ']

        smiles = standardise.run(r'{}'.format(smiles))
        data = self.smiles2graph(r'{}'.format(smiles))
        data.batch = zeros(data.num_nodes, dtype=long)

        for task in tasks[1:]:
            state_dict = load(compl_root / 'complementary/{}/state_dict.pt'.format(task))
            hyperparams = state_dict['hyper_parameters']
            compl_model = EGConvNet(
                hyperparams['hidden_channels'],
                hyperparams['num_layers'],
                hyperparams['num_heads'],
                hyperparams['num_bases'],
                aggregator=['sum', 'mean', 'max'])
            compl_model.load_state_dict(state_dict['state_dict'])
            compl_model.eval()

            output = compl_model(data.x, data.edge_index, data.batch).detach().cpu().numpy()[0][0]
            if task in classification_tasks:
                output = round(((1 / (1 + np.exp(-output)))), 2)
            else:
                output = round(output, 2)
            predictions.append(output.astype(float))

        test_example = pd.DataFrame(columns=tasks, data=[predictions], index=[0])

        xgb_file = open(compl_root / 'complementary/xgb_classifier_reduced.pkl', 'rb')
        xgb_model = pickle.load(xgb_file)
        ntree_limit = xgb_model.get_booster().best_ntree_limit

        prediction = int(xgb_model.predict(test_example, ntree_limit=ntree_limit)[0])

        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer(test_example)

        """
        test_example.rename(columns={'Clearance_Hepatocyte_AZ': 'Clearance Hepatocyte',
                                     'Bioavailability_Ma': 'Bioavailability',
                                     'CYP2C9_Substrate_CarbonMangels': 'CYP2C9 Substrate',
                                     'predict_withdrawn': 'Predict withdrawn'}, inplace=True)
        """

        test_example.rename(columns={'Clearance_Hepatocyte_AZ': 'Excretion',
                                     'Bioavailability_Ma': 'Absorption',
                                     'CYP2C9_Substrate_CarbonMangels': 'Metabolism',
                                     'predict_withdrawn': 'Withdrawn prediction',
                                     'nr-ppar-gamma': 'Toxicity'}, inplace=True)

        plot_values = pd.DataFrame(columns=test_example.columns, data=shap_values.values).transpose().reset_index()
        px = 1 / plt.rcParams['figure.dpi']
        fig, ax = plt.subplots(figsize=(300 * px, 500 * px))
        ax = sns.barplot(data=plot_values, x=0, y='index')
        ax.set_xlabel("SHAP value")
        ax.set_ylabel("")
        ax.xaxis.label.set_color('#66615b')
        plt.xticks()
        ax.tick_params(axis='x', colors='#66615b')
        ax.tick_params(axis='y', colors='#66615b')
        last_position = [0]
        for i, bar in enumerate(ax.patches):
            x = bar.get_x()
            last_position.append(x)
            if bar.get_width() < 0:
                bar.set_color("#86d9ab")
                bar.set_x(last_position[i] + x)
            else:
                bar.set_color("#f33816")
        ax.set_box_aspect(3 / len(ax.patches))
        img = StringIO()
        fig.savefig(img, format='svg', bbox_inches="tight")
        img = img.getvalue()
        plt.close()

        return prediction, dict(zip(tasks, predictions)), img






