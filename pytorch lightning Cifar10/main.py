import pytorch_lightning as torchl
from pytorch_lightning.loggers import WandbLogger
import torch
import torchvision
import torchmetrics

class CIFAR10MODEL(torchl.LightningModule):
  def __init__(self):
      super().__init__()
      self.conv1 = torch.nn.Conv2d(3, 6, 5)
      self.pool = torch.nn.MaxPool2d(2, 2)
      self.conv2 = torch.nn.Conv2d(6, 16, 5)
      self.fc1 = torch.nn.Linear(16 * 5 * 5, 120)
      self.fc2 = torch.nn.Linear(120, 84)
      self.fc3 = torch.nn.Linear(84, 10)
      self.accuracy = torchmetrics.Accuracy()
        
  def forward(self, x):
      x = self.pool(torch.nn.functional.relu(self.conv1(x)))
      x = self.pool(torch.nn.functional.relu(self.conv2(x)))
      x = x.view(-1, 16 * 5 * 5)
      x = torch.nn.functional.relu(self.fc1(x))
      x = torch.nn.functional.relu(self.fc2(x))
      x = self.fc3(x)
      return x
  def training_step(self, batch, batch_idx):
      inp,label = batch
      outputs = self(inp)
      loss_func = torch.nn.CrossEntropyLoss()
      loss=loss_func(outputs,label)
      #loss
      self.log('train_loss', loss,prog_bar=True)
      #정확도
      self.log('train_acc', self.accuracy(outputs, label),prog_bar=True)
      return loss

  def validation_step(self, batch, batch_idx):
      inp,label = batch
      outputs = self(inp)
      loss_func = torch.nn.CrossEntropyLoss()
      loss=loss_func(outputs,label)
      #loss
      self.log('valid_loss', loss,prog_bar=True)
      #정확도
      self.log('valid_acc', self.accuracy(outputs, label),prog_bar=True)
      return loss

  def test_step(self, batch, batch_idx):
      inp,label = batch
      outputs = self(inp)
      loss_func = torch.nn.CrossEntropyLoss()
      loss=loss_func(outputs,label)
      #loss
      self.log('test_loss', loss,prog_bar=True)
      #정확도
      self.log('test_acc', self.accuracy(outputs, label),prog_bar=True)
      return loss

  def configure_optimizers(self):
      optimizer = torch.optim.Adam(self.parameters(), lr=0.01)
      return optimizer

class CIFAR10DATA(torchl.LightningDataModule):
  def __init__(self,batch_size=16):
    super().__init__()
    self.batch_size=batch_size
  def prepare_data(self):
    torchvision.datasets.CIFAR10("./",train=True,download=True)
    torchvision.datasets.CIFAR10("./",train=False,download=False)
  def setup(self, stage=None):        
      now_transform = torchvision.transforms.Compose([
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])

      if stage == 'fit' or stage is None:
          cifar_train = torchvision.datasets.CIFAR10("./", train=True,transform=now_transform)
          self.cifar_train, self.cifar_val = torch.utils.data.random_split(cifar_train, [45000, 5000])
      if stage == 'test' or stage is None:
          self.cifar_test = torchvision.datasets.CIFAR10("./", train=False,transform=now_transform)
    
  def train_dataloader(self):
      return torch.utils.data.DataLoader(self.cifar_train, batch_size=self.batch_size, shuffle=True)

  def val_dataloader(self):
      return torch.utils.data.DataLoader(self.cifar_val, batch_size=self.batch_size)

  def test_dataloader(self):
      return torch.utils.data.DataLoader(self.cifar_test, batch_size=self.batch_size)

wandb_logger = WandbLogger(name='test1',project='20161215051_이상재_pytorch lightning Cifar10')
cfdata=CIFAR10DATA()
cfdata.prepare_data()
cfdata.setup()
cfmodel=CIFAR10MODEL()
trainer = torchl.Trainer(
    logger=wandb_logger,
    gpus=-1,    
    max_epochs=50 
    )
trainer.fit(cfmodel,cfdata)
trainer.test(cfmodel,cfdata)
