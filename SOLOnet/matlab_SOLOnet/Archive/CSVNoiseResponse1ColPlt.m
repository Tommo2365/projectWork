% get file
matArray = csvread(uigetfile);

% formatSpec = '%f'; %format text file to single point (col = 1)

% prompt box
prompt = {'Name of experment: Noise/Response', 'Serial number:', 'Enter furnace set point Temperature:'};
dlgtitle = 'Input Vaule';
bootInput = inputdlg(prompt); % input
pltName = string(bootInput{1}); % convert eleemnt 2 into string
SN = string(bootInput{2}); % serial number for save file name
tempValue = string(bootInput{3}); % convert element 2 into string (number)

% declae array
% n = fscanf(inFile,formatSpec); % use for txt files
yArray = matArray(:, 1);
L = length(yArray);
xArray = [1:1:L].';

% show standard deviation in command window
stdDev = std(yArray);

% settiing parameters for axis
xMaxVal = max(xArray);
xMinVal = min(xArray);

yMaxVal = max(yArray);
yMinVal = min(yArray);

yMaxPara = yMaxVal + 1;
yMinPara = yMinVal - 1;

yMedVal = median(yArray) - 10; % adjust integer to see more of y axis

% save file as xlsx

% flip y-axis data upside down
yAxis = flipud(yArray);

A = [xArray, yArray];

if pltName = Response
    fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.xlsx');
    xlswrite(fileName, A);
elseif pltName = Noise
    fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.xlsx');
    xlswrite(fileName, A);
end
    
% make a plot
scatter(xArray, yAxis);
grid on;
title([pltName + ' at ' + tempValue + 'ºC']);
xlabel('Time / {\it s}');
ylabel('SOLOnet Temperature Reading / {\it ºC}');
legend('StdDev:', num2str(stdDev));
xlim([0 xMaxVal + 1]);

% conditions for Noise or Response axis
if (yMaxVal - yMinVal) > 40    % if these condidtions are met
    ylim([yMedVal yMaxPara]);  % use median to find approriate axis
else
    ylim([yMinPara yMaxPara]); % else use these parameters
end

% write file name a savefig
if pltName = Response
    figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.fig');
    savefig(figName)
elseif pltName = Noise
    figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.fig');
    savefig(figName)
end

