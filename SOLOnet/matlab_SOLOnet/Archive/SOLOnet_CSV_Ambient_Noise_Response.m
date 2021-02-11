% get file
matArray = csvread(uigetfile);

% Change this value to increase or decreas y-axis for response time
yResponseSubVal = 40    

% prompt box
prompt = {'Name of experment: Noise/Response/Ambient', 'Serial number:', 'Enter furnace set point Temperature:'};
dlgtitle = 'Input Vaule';
bootInput = inputdlg(prompt); % input
pltName = string(bootInput{1}); % convert eleemnt 2 into string
SN = string(bootInput{2}); % serial number for save file name
tempValue = string(bootInput{3}); % convert element 2 into string (number)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  NOISE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if pltName == 'Noise'
    % declae array
    % n = fscanf(inFile,formatSpec); % use for txt files
    yArray = matArray(:, 1);
    L = length(yArray);
    xArray = [1:1:L].';

    % show standard deviation in command window
    stdDev = num2str(std(yArray));

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

    if pltName == 'Response'
        fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.xlsx');
        xlswrite(fileName, A);
    elseif pltName == 'Noise'
        fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.xlsx');
        xlswrite(fileName, A);
    end
    
    % make a plot
    scatter(xArray, yAxis);
    grid on;
    title([pltName + ' at ' + tempValue + 'ºC']);
    xlabel('Time / {\it s}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}');
    legend('StdDev:', stdDev);
    xlim([0 xMaxVal + 1]);

    % conditions for Noise or Response axis
    if (yMaxVal - yMinVal) > yResponseSubVal    % if these condidtions are met
        ylim([yMedVal yMaxPara]);  % use median to find approriate axis
    else
        ylim([yMinPara yMaxPara]); % else use these parameters
    end

    % write file name a savefig
    if pltName == 'Response'
        figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.fig');
        savefig(figName)
    elseif pltName == 'Noise'
        figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.fig');
        savefig(figName)
    end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  RESPONSE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 

elseif pltName == 'Response'
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

    if pltName == 'Response'
        fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.xlsx');
        xlswrite(fileName, A);
    elseif pltName == 'Noise'
        fileName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.xlsx');
        xlswrite(fileName, A);
    end
    
    % make a plot
    scatter(xArray, yAxis);
    grid on;
    title([pltName + ' at ' + tempValue + 'ºC']);
    xlabel('Time / {\it s}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}');
    %%legend('StdDev:', num2str(stdDev));
    xlim([0 xMaxVal + 1]);

    % conditions for Noise or Response axis
    if (yMaxVal - yMinVal) > yResponseSubVal    % if these condidtions are met
        ylim([yMedVal yMaxPara]);  % use median to find approriate axis
    else
        ylim([yMinPara yMaxPara]); % else use these parameters
    end

    % write file name a savefig
    if pltName == 'Response'
        figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', SN, '.fig');
        savefig(figName)
    elseif pltName == 'Noise'
        figName = sprintf( '%s', datestr(now,'yyyymmdd_HH_MM_SS_'), pltName,'_', tempValue,'C_' ,SN, '.fig');
        savefig(figName)
    end
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  AMBIENT  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

elseif pltName == 'Ambient'
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

end