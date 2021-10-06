from pathlib import Path
import numpy as np
import pandas as pd
from matplotlib import pyplot
from networkx.readwrite import json_graph
from rdkit import Chem, RDConfig
from rdkit.Chem import HybridizationType, ChemicalFeatures
from torch_geometric.data import Data
from torch_geometric.nn import EGConv, global_mean_pool, GNNExplainer
from torch.nn import Sequential, BatchNorm1d, ReLU, Linear, Module, ModuleList
from torch import load, Tensor, long, zeros
from torch_geometric.utils import to_networkx
from json import dumps

fdef_name = Path(RDConfig.RDDataDir) / 'BaseFeatures.fdef'
factory = ChemicalFeatures.BuildFeatureFactory(str(fdef_name))

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

        mol = Chem.MolFromSmiles(r'{}'.format(data))

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

        return output, predicted_class, round(approved_p_value, 2), round(withdrawn_p_value, 2)

    def explain(self, smiles, threshold=0, epochs=300):
        features = ["is_boron", "is_carbon", "is_nitrogen", "is_oxygen", "is_flourine", "is_phosporus", "is_sulfur",
                    "is_chlorine", "is_bromine", "is_iodine", "is_other", "zero_Hs", "one_H", "two_Hs", "three_Hs",
                    "four_Hs", "is_s", "is_sp", "is_sp2", "is_sp3", "is_sp3d", "is_sp3d2", "unspecified_hybr",
                    "is_inring", "is_aromatic", "is_donor", "is_acceptor"]

        explainer = GNNExplainer(self.model, epochs=epochs)
        data = self.smiles2graph(r'{}'.format(smiles))
        data.batch = zeros(data.num_nodes, dtype=long)
        node_feat_mask, edge_mask = explainer.explain_graph(data.x, data.edge_index)
        edge_mask = edge_mask.detach().numpy()
        node_feat_mask = node_feat_mask.detach().numpy()
        edge_mask = edge_mask / edge_mask.max()
        edge_mask = np.where(edge_mask > threshold, 1, 0).tolist()
        viridis = pyplot.cm.get_cmap('YlOrRd')
        color_map = []
        for i in edge_mask:
            color = viridis(i)
            color_map.append(color)
        graph = Data(
            x=data.x,
            edge_index=data.edge_index,
            edge_attrs=color_map,
            node_labels=data.feature_names.tolist(),
        )
        g = to_networkx(graph, to_undirected=True, edge_attrs=['edge_attrs'], node_attrs=['node_labels'])
        for i in g.nodes:
            g.nodes[i]['atom'] = g.nodes[i]['node_labels'][0]

        node_feat_importance = pd.DataFrame(
            data=node_feat_mask[np.newaxis], columns=features, index=[0]
        ).to_json(
            index=False,
            orient='split'
        )
        graph_json = json_graph.node_link_data(g)
        graph_json = dumps(graph_json)

        return graph_json, node_feat_importance




