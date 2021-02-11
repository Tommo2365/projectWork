% get file
matArray = csvread(uigetfile);

% prompt box
prompt = {'Enter furnace temperature(Cyclops):', 'Number of steps:', 'Serial number:'};

%dlgtitle = 'Input Vaule';
input = inputdlg(prompt); % input
tempValue = str2num(input{1}); % convert element 'N' into number
stepCount = str2num(input{2});
SN = input{3};                 % for use in save file name

% declare array (:, axis number)
xAxis = matArray(:, 1);
yAxis = matArray(:, 2);

% set up condtions
xSum = sum(xAxis);
eSum = sum(yAxis);

% swap columns if conditions are met
if (xSum > eSum)
    yAxis = matArray(:, 1);
    xAxis = matArray(:, 2);
end

% subtract furnTemp from yAxis 
if yAxis == matArray(:, 1);
    Error = yAxis - tempValue;
elseif xAxis == matArray(:, 1);
    Error = yAxis - tempValue;
end

% flip columns upisded down (data input is formated upside down prior)
x = flipud(xAxis);
yn = flipud(yAxis);
y = flipud(Error);

% Find the maximum drift
driftError = max(y)-min(y);
driftError2 = num2str(driftError);

% combine matrix axis
A = [x,yn,y]; 

% write file names and save data as xlsx
if stepCount >= 2
  Filename = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_STEP_', SN, '.xlsx' );
  xlswrite(Filename, A);
elseif stepCount < 2
    Filename = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_', SN, '.xlsx' );
    xlswrite(Filename, A);
end

% write file names and save plt as .fig
if stepCount >= 2
    figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_STEP_', SN, '.fig');
elseif stepCount < 2
    figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_', SN, '.fig');
end
%figJPG = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), 'Ambient_', SN, '.jpg');

% plot data
figure1 = figure;
drift = scatter(x, y);
grid on;
hold on
e1 = plot([5 50], [3 -7], 'LineWidth',2);
e1.Color = 'r';
hold on
e2 = plot([5 50], [-3 7], 'LineWidth',2);
e2.Color = 'r';
legend1 = legend('Drift','Spec','Spec');
set(legend1,'Position',[0.85362164058084 0.505700114698771 0.127009644960667 0.119638822955956]);
title('Ambient Response');
xlabel('Ambient (get) / {\it ºC}');
ylabel('Error / {\it ºC}' );

% add text to plot
annotation(figure1,'textbox',...
    [0.850852466225819 0.197951711165462 0.0878477282003988 0.138248844263924],...
    'String',{'Number of steps:',(input{2}), '', 'Max Drift Error / {\it ºC}:',driftError2},...
    'FitBoxToText','on',...
    'FontWeight','bold',...
    'FontSize',9);

savefig(figName);
%savefig(figJPG)