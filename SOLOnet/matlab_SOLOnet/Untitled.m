rFig1 = subplot(1,2,1)
    scatter(xArray, yAxis);
    grid on;
    title([pltName,' at ',tempValue,'ºC']);
    xlabel('Time / {\it s}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}');
    %%legend('StdDev:', num2str(stdDev));
    xlim([0 120]);
    
    
    % make a plot
    rFig2 = subplot(1,2,2)
    scatter(xArray, yAxis);
    grid on;
    title([pltName,' at ',tempValue,'ºC']);
    xlabel('Time / {\it s}');
    ylabel('SOLOnet Temperature Reading / {\it ºC}');
    xlim([0 120]);
    ylim([yMedVal yMaxPara]);  % use median to find approriate axi