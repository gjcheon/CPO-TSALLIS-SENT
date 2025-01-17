from torch.nn import functional
from torch import jit, nn
import torch

LOG_STD_MAX = 2
LOG_STD_MIN = -4
EPS = 1e-8

def initWeights(m, init_value=0.0):
    if isinstance(m, torch.nn.Linear):
        m.weight.data.normal_(0, 0.01)
        m.bias.data.normal_(init_value, 0.01)

class Policy(nn.Module):
    def __init__(self, args):
        super(Policy, self).__init__()

        self.state_dim = args.obs_dim + args.n_skills
        self.action_dim = args.action_dim
        self.hidden1_units = args.hidden_dim
        self.hidden2_units = args.hidden_dim
        self.log_std_init = args.log_std_init
        self.activation = args.activation

        self.fc1 = nn.Linear(self.state_dim, self.hidden1_units)
        self.fc2 = nn.Linear(self.hidden1_units, self.hidden2_units)
        self.act_fn = eval(f'torch.nn.{self.activation}()')
        self.output_act_fn = torch.sigmoid

        self.fc_mean = nn.Linear(self.hidden2_units, self.action_dim)
        self.fc_log_std = nn.Linear(self.hidden2_units, self.action_dim)


    def forward(self, x):
        x = self.act_fn(self.fc1(x))
        x = self.act_fn(self.fc2(x))
        mean = self.output_act_fn(self.fc_mean(x))
        log_std = self.fc_log_std(x)
        log_std = torch.clamp(log_std, min=LOG_STD_MIN, max=LOG_STD_MAX)
        std = torch.exp(log_std)
        return mean, log_std, std

    def initialize(self):
        for m_idx, module in enumerate(self.children()):
            if m_idx != 4:
                module.apply(initWeights)
            else:
                module.apply(lambda m: initWeights(m=m, init_value=self.log_std_init))


class Value(nn.Module):
    def __init__(self, args):
        super(Value, self).__init__()

        self.obs_dim = args.obs_dim + args.n_skills
        self.action_dim = args.action_dim
        self.hidden1_units = args.hidden_dim
        self.hidden2_units = args.hidden_dim
        self.activation = args.activation

        self.fc1 = nn.Linear(self.obs_dim, self.hidden1_units)
        self.fc2 = nn.Linear(self.hidden1_units, self.hidden2_units)
        self.fc3 = nn.Linear(self.hidden2_units, 1)
        self.activ = eval(f'torch.nn.{self.activation}()')


    def forward(self, x):
        x = self.activ(self.fc1(x))
        x = self.activ(self.fc2(x))
        x = self.fc3(x)
        x = torch.reshape(x, (-1,))
        return x

    def initialize(self):
        self.apply(initWeights)


class Value2(nn.Module):
    def __init__(self, args):
        super(Value2, self).__init__()

        self.obs_dim = args.obs_dim + args.n_skills
        self.action_dim = args.action_dim
        self.hidden1_units = args.hidden_dim
        self.hidden2_units = args.hidden_dim
        self.activation = args.activation

        self.fc1 = nn.Linear(self.obs_dim, self.hidden1_units)
        self.fc2 = nn.Linear(self.hidden1_units, self.hidden2_units)
        self.fc3 = nn.Linear(self.hidden2_units, 1)
        self.activ = eval(f'torch.nn.{self.activation}()')
        self.out_activ = torch.nn.Softplus()


    def forward(self, x):
        x = self.activ(self.fc1(x))
        x = self.activ(self.fc2(x))
        x = self.out_activ(self.fc3(x))
        x = torch.reshape(x, (-1,))
        return x

    def initialize(self):
        self.apply(initWeights)

def init_weight(layer, initializer="he normal"):
    if initializer == "xavier uniform":
        nn.init.xavier_uniform_(layer.weight)
    elif initializer == "he normal":
        nn.init.kaiming_normal_(layer.weight)

class Discriminator(nn.Module):
    def __init__(self, args):
        super(Discriminator, self).__init__()
        self.obs_dim = args.obs_dim
        self.n_skills = args.n_skills
        self.hidden_dim = args.hidden_dim
        self.activation = args.activation

        self.hidden1 = nn.Linear(self.obs_dim, self.hidden_dim)
        init_weight(self.hidden1)
        self.hidden1.bias.data.zero_()
        self.hidden2 = nn.Linear(self.hidden_dim, self.hidden_dim)
        init_weight(self.hidden2)
        self.hidden2.bias.data.zero_()
        self.q = nn.Linear(self.hidden_dim, self.n_skills)
        init_weight(self.q, initializer="xavier uniform")
        self.q.bias.data.zero_()
        self.activ = eval(f'torch.nn.{self.activation}()')

    def forward(self, states):
        x = self.activ(self.hidden1(states))
        x = self.activ(self.hidden2(x))
        logits = self.q(x)
        return logits