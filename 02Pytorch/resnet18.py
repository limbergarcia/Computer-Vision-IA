import torch
import torch.utils.data
from torchvision import transforms, datasets
import torchvision
import time
from matplotlib import pyplot as plt
import os

if __name__ == '__main__':
    transforms_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    transforms_test = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.CenterCrop((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) 
    ])

    train_dir = "skin_cancer_dataset/train"
    test_dir = "skin_cancer_dataset/test"

    train_dataset = datasets.ImageFolder(train_dir, transforms_train)
    test_dataset = datasets.ImageFolder(test_dir, transforms_test)

    train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=12, shuffle=True, num_workers=0)
    test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=12, shuffle=False, num_workers=0)

    model = torchvision.models.resnet34(pretrained=False)

    # Cargar los pesos preentrenados guardados
    model.load_state_dict(torch.load('./resnet34-weights.pth'))

    num_features = model.fc.in_features
    model.fc = torch.nn.Linear(num_features, 2)
    model = model.to('cuda')

    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)

    train_loss = []
    train_accuracy = []
    test_loss = []
    test_accuracy = []

    num_epochs = 10
    start_time = time.time()

    for epoch in range(num_epochs):
        print("Epoch {} running".format(epoch))
        """ Training Phase """
        model.train()
        running_loss = 0.0
        running_corrects = 0

        for i, (inputs, labels) in enumerate(train_dataloader):
            inputs = inputs.to('cuda')
            labels = labels.to('cuda')

            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            running_corrects += torch.sum(preds == labels.data).item()

        epoch_loss = running_loss / len(train_dataset)
        epoch_acc = running_corrects / len(train_dataset) * 100

        train_loss.append(epoch_loss)
        train_accuracy.append(epoch_acc)

        print('[Train #{}] Loss: {:.4f} Accuracy: {:.4f}% Time: {:.4f}s'.format(epoch, epoch_loss, epoch_acc, time.time() - start_time))

        model.eval()
        with torch.no_grad():
            running_loss = 0.0
            running_corrects = 0
            for inputs, labels in test_dataloader:
                inputs = inputs.to('cuda')
                labels = labels.to('cuda')
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)
                running_loss += loss.item()
                running_corrects += torch.sum(preds == labels.data).item()

            epoch_loss = running_loss / len(test_dataset)
            epoch_acc = running_corrects / len(test_dataset) * 100

            test_loss.append(epoch_loss)
            test_accuracy.append(epoch_acc)

        print('[Test #{}] Loss: {:.4f} Accuracy: {:.4f}% Time: {:.4f}s'.format(epoch, epoch_loss, epoch_acc, time.time() - start_time))

    # Plotting the results
    plt.plot(train_loss, label='Training Loss')
    plt.plot(test_loss, label='Test Loss')
    plt.legend()
    plt.show()

    plt.plot(train_accuracy, label='Training Accuracy')
    plt.plot(test_accuracy, label='Test Accuracy')
    plt.legend()
    plt.show()