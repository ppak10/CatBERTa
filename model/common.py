import torch, os, shutil
from transformers import (RobertaConfig, RobertaModel)
from model.regressors import (MyModel, MyModel2, 
                              MyModel_MLP, MyModel_MLP2,
                              MyModel_AttnHead, 
                              MyModel_ConcatLast4Layers)
from model.classifiers import MultiLabelClassifier

def backbone_wrapper(backbone, head_type):
    '''
    Wrapper function to add a head to the backbone roberta model
    backbone: RobertaModel (base or pretrained)
    head_type: str, type of head to add to the backbone
    '''

    if head_type == "pooler":
        model = MyModel(backbone) 
    elif head_type == "mlp":
        model = MyModel_MLP(backbone)
    elif head_type == "mlp2":
        model = MyModel_MLP2(backbone)
    elif head_type == "attnhead":
        model = MyModel_AttnHead(backbone)
    elif head_type == "concatlayer":
        model = MyModel_ConcatLast4Layers(backbone)
    elif head_type == "multilabel":
        model = MultiLabelClassifier(backbone)
    else:
        raise ValueError(f"Unknown model_head: {head_type}") 
    
    return model

def checkpoint_loader(model, checkpoint_path, load_on_roberta=False):
    '''
    Load checkpoint to model
    model: RobertaModel (base or with head)
    checkpoint_path: path to checkpoint
    load_on_roberta: whether to load checkpoint on roberta_model or the whole model with head
    '''
    model_dict = model.state_dict()
    state_dict = torch.load(checkpoint_path)
    if load_on_roberta:
        # this is option is to load the checkpoint on the roberta_model
        # in this case, the checkpoint should be from pretraining
        matching_state_dict = {k.replace('roberta_model.', ''): v for k, v in state_dict.items() if k.replace('roberta_model.', '') in model_dict}
    else:
        # this is option is to continue training on the whole model with head
        matching_state_dict = {k: v for k, v in state_dict.items() if k in model_dict}
    
    if matching_state_dict.keys() == model_dict.keys():
        print('All keys matched!')
    else:
        print('Some keys did not match!')

    model.load_state_dict(matching_state_dict, strict=False)
    return model